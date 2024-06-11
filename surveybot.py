import re
import sys
import os
from systemd import journal
import gspread
from google.oauth2.service_account import Credentials
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
import telebot
import mariadb
from datetime import datetime
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

dir = os.path.dirname(__file__)
TOKEN='7337592356:AAF2HKa_40Ikaaa4ICTWJ5guOlc6ozyWkPA'
#TOKEN = os.environ['S_TOKEN']
bot = telebot.TeleBot(TOKEN)

variables={}
BOT_NAME='customsurveybot'

try:
    conn = mariadb.connect(
        user="wordlerbot",
        password="i4mp455w0rd_",
        host="localhost",
        database="bot_db"

    )
    journal.write(f"Connected well")
    cur = conn.cursor()
except mariadb.Error as e:
    journal.write(f"Error connecting to MariaDB Platform: {e}")
    sys.exit(1)

def set_keyboard(buttons_list):
    w=2
    buttons = [telebot.types.KeyboardButton(i) for i in buttons_list]
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=w, resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(*buttons)
    
    return keyboard


#init gspread
scopes = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive']
credentials = Credentials.from_service_account_file(os.getcwd()+'/config.json', scopes=scopes)
gc = gspread.authorize(credentials)
gauth = GoogleAuth()
drive = GoogleDrive(gauth)

def write_to_sheet(spread_name, values, list_name='Лист1'):
    gs = gc.open_by_key(spread_name)
    sheet = gs.worksheet(list_name)
    sheet.append_row(values=values, value_input_option='USER_ENTERED')

#commented out is part to read the chat

'''@bot.message_handler(content_types=[
    "new_chat_members"
])

def a(message):
    journal.write(f"Smth was added: {message.json['new_chat_participant']['username']}")
    if (message.json['new_chat_participant']['username'] == BOT_NAME):
        a_a(message)

@bot.message_handler(func=lambda message: True)

def a_a(message):
    chat_id = message.chat.id
    name=' '.join(filter(None, (message.from_user.first_name, message.chat.last_name)))
    print(f"{name} says {message.text}")
    write_to_sheet(spread_name='197EttuqtGNd_C1hMuZpA658G9nbpLeusRRlFnXcmnrk', values=[name, message.text, str(datetime.now())])
'''    


@bot.message_handler(commands=['start', 'go'])

def start_handler(message):
    chat_id = message.chat.id
    name=' '.join(filter(None, (message.chat.first_name, message.chat.last_name)))
    try:
        
        cur.execute(
    "INSERT INTO surveybot_users (id, name, last_visited, alias) VALUES (?, ?, ?, ?) ON DUPLICATE KEY UPDATE last_visited=?", 
    (chat_id, name, datetime.now(), message.chat.username, datetime.now()) )
        conn.commit()
    except mariadb.Error as e:
        journal.write(f"Error in db: {e}") 

    variables[chat_id] = {}

    try:
        
        cur.execute(
    "select * from surveybot_surveys", 
    )
        variables[chat_id]['surveys']=cur.fetchall()
        variables[chat_id]['pointer']=-1
    except mariadb.Error as e:
        journal.write(f"Error in db: {e}") 

    
    
    msg = bot.send_message(chat_id, 'Выберите опрос из списка:', reply_markup=set_keyboard([i[2] for i in variables[chat_id]['surveys']]))

    bot.register_next_step_handler(msg, question)

def question(message):
    chat_id = message.chat.id
    text = message.text
    if (message.text == '/start'):
        start_handler(message)
        return
    #first question
    if (variables[chat_id]['pointer']==-1):
        cur.execute(
        "select * from surveybot_surveys where header=?", 
        (message.text,) )
        f=cur.fetchone()
        variables[chat_id]['curr_survey_id']=f[0]
        variables[chat_id]['gdoc']=f[3]
        variables[chat_id]['final']=f[4]
        variables[chat_id]['answers']=[]
        variables[chat_id]['correctness']=[]
        cur.execute(
        "select q.*, count(*) over() from surveybot_questions q where survey_id=?", 
        (variables[chat_id]['curr_survey_id'],) )
        variables[chat_id]['all_questions']=cur.fetchall()
        variables[chat_id]['survey_len']=variables[chat_id]['all_questions'][0][7]
    reply=[]
    if(variables[chat_id]['pointer']>=0):
        variables[chat_id]['answers'].append(message.text)
        variables[chat_id]['correctness'].append(1)
        
        if (variables[chat_id]['all_questions'][variables[chat_id]['pointer']][6] != None):
            variables[chat_id]['correctness'][variables[chat_id]['pointer']]= 1 if (variables[chat_id]['all_questions'][variables[chat_id]['pointer']][6] == message.text) else 0
    variables[chat_id]['pointer']=variables[chat_id]['pointer']+1
    if (variables[chat_id]['pointer']>=variables[chat_id]['survey_len']):
        bot.send_message(chat_id, variables[chat_id]['final'].format(results=variables[chat_id]['correctness']))
        write_to_sheet(variables[chat_id]['gdoc'], [' '.join(filter(None, (message.chat.first_name, message.chat.last_name))),*(variables[chat_id]['answers'])])
        bot.send_message(chat_id, 'Нажмите /start, чтобы пройти другой опрос.')
        return
    if (variables[chat_id]['all_questions'][variables[chat_id]['pointer']][5] != None):
        reply=variables[chat_id]['all_questions'][variables[chat_id]['pointer']][5].split(',')
    msg=bot.send_message(chat_id,variables[chat_id]['all_questions'][variables[chat_id]['pointer']][3], reply_markup=set_keyboard(reply))
    bot.register_next_step_handler(msg, question)

        
bot.polling(none_stop=True)