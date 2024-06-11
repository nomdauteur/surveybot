-- bot_db.routelebot_users definition

CREATE TABLE `surveybot_users` (
  `id` bigint(20) NOT NULL,
  `name` varchar(1000) DEFAULT NULL,
  `last_visited` datetime(6) DEFAULT NULL,
  `alias` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `surveybot_surveys` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `name` varchar(1000) DEFAULT NULL,
  `header` varchar(1000) DEFAULT NULL,
  `gspread_token` varchar(1000) DEFAULT NULL,
  `final_text` varchar(2000) DEFAULT NULL,
  PRIMARY KEY (`id`)
);

CREATE TABLE `surveybot_questions` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `survey_id` bigint(20) NOT NULL,
  `question_number` bigint(20) NOT NULL,
  `question_text` varchar(1000) DEFAULT NULL,
  `shortname` varchar(1000) DEFAULT NULL,
  `answers` varchar(1000) DEFAULT NULL,
  `correct_answer` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`id`)
);

