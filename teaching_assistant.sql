# Host: localhost  (Version: 5.7.26)
# Date: 2025-11-21 23:06:25
# Generator: MySQL-Front 5.3  (Build 4.234)

/*!40101 SET NAMES utf8 */;

#
# Structure for table "assigned_questions"
#

DROP TABLE IF EXISTS `assigned_questions`;
CREATE TABLE `assigned_questions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `student_id` int(11) NOT NULL,
  `question_id` int(11) NOT NULL,
  `position` int(11) NOT NULL,
  `session_id` int(11) DEFAULT NULL,
  `assigned_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` int(11) DEFAULT NULL,
  `school_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `student_id` (`student_id`),
  KEY `question_id` (`question_id`),
  KEY `school_id` (`school_id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

#
# Data for table "assigned_questions"
#

/*!40000 ALTER TABLE `assigned_questions` DISABLE KEYS */;
INSERT INTO `assigned_questions` VALUES (1,104,3,1,NULL,'2025-11-21 13:37:12',NULL,NULL);
/*!40000 ALTER TABLE `assigned_questions` ENABLE KEYS */;

#
# Structure for table "classes"
#

DROP TABLE IF EXISTS `classes`;
CREATE TABLE `classes` (
  `class_id` int(11) NOT NULL AUTO_INCREMENT,
  `class_name` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `school_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`class_id`),
  KEY `school_id` (`school_id`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

#
# Data for table "classes"
#

/*!40000 ALTER TABLE `classes` DISABLE KEYS */;
INSERT INTO `classes` VALUES (2,'2班',NULL,NULL),(4,'4班',NULL,NULL),(5,'5班',NULL,NULL);
/*!40000 ALTER TABLE `classes` ENABLE KEYS */;

#
# Structure for table "conversations"
#

DROP TABLE IF EXISTS `conversations`;
CREATE TABLE `conversations` (
  `conversation_id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `title` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `school_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`conversation_id`),
  KEY `school_id` (`school_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

#
# Data for table "conversations"
#

/*!40000 ALTER TABLE `conversations` DISABLE KEYS */;
/*!40000 ALTER TABLE `conversations` ENABLE KEYS */;

#
# Structure for table "messages"
#

DROP TABLE IF EXISTS `messages`;
CREATE TABLE `messages` (
  `message_id` int(11) NOT NULL AUTO_INCREMENT,
  `conversation_id` int(11) NOT NULL,
  `sender` enum('user','ai') NOT NULL,
  `content` longtext,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`message_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

#
# Data for table "messages"
#

/*!40000 ALTER TABLE `messages` DISABLE KEYS */;
/*!40000 ALTER TABLE `messages` ENABLE KEYS */;

#
# Structure for table "questions"
#

DROP TABLE IF EXISTS `questions`;
CREATE TABLE `questions` (
  `question_id` int(11) NOT NULL AUTO_INCREMENT,
  `difficulty_level` enum('easy','medium','difficult') CHARACTER SET utf8 DEFAULT NULL,
  `topic` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `topic_id` int(11) DEFAULT NULL,
  `question_text` text COLLATE utf8_unicode_ci,
  `question_image` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `answer_text` text COLLATE utf8_unicode_ci,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `group_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`question_id`)
) ENGINE=MyISAM AUTO_INCREMENT=10 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

#
# Data for table "questions"
#

/*!40000 ALTER TABLE `questions` DISABLE KEYS */;
INSERT INTO `questions` VALUES (1,'easy','函数与图像',101,'已知函数 f(x) = 2x^2 - 4x + 3，判断其在区间 [-1, 3] 上的单调性，并说明理由。','https://via.placeholder.com/360x180?text=函数图像','函数为开口向上的抛物线，顶点在 x=1，区间 [-1,3] 包含顶点，需分区间分析。','2025-11-21 21:27:55',NULL),(2,'easy','函数与图像',101,'已知函数 f(x) = 2x^2 - 4x + 3，判断其在区间 [-1, 3] 上的单调性，并说明理由。','https://via.placeholder.com/360x180?text=函数图像','函数为开口向上的抛物线，顶点在 x=1，区间 [-1,3] 包含顶点，需分区间分析。','2025-11-21 22:13:43',NULL);
/*!40000 ALTER TABLE `questions` ENABLE KEYS */;

#
# Structure for table "schools"
#

DROP TABLE IF EXISTS `schools`;
CREATE TABLE `schools` (
  `school_id` int(11) NOT NULL AUTO_INCREMENT,
  `school_name` varchar(200) NOT NULL,
  PRIMARY KEY (`school_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

#
# Data for table "schools"
#


#
# Structure for table "source_questions"
#

DROP TABLE IF EXISTS `source_questions`;
CREATE TABLE `source_questions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `exam_type` enum('monthly','final','midterm','gaokao','mock','other') NOT NULL,
  `exam_year` int(11) DEFAULT NULL,
  `exam_region` varchar(50) DEFAULT NULL,
  `question_no` varchar(20) DEFAULT NULL,
  `question_stem` text NOT NULL,
  `answer` text,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `group_id` int(11) DEFAULT NULL,
  `school_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `school_id` (`school_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

#
# Data for table "source_questions"
#

/*!40000 ALTER TABLE `source_questions` DISABLE KEYS */;
/*!40000 ALTER TABLE `source_questions` ENABLE KEYS */;

#
# Structure for table "students"
#

DROP TABLE IF EXISTS `students`;
CREATE TABLE `students` (
  `student_id` int(11) NOT NULL AUTO_INCREMENT,
  `class_id` int(11) DEFAULT NULL,
  `student_name` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `school_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`student_id`),
  KEY `class_id` (`class_id`),
  KEY `school_id` (`school_id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

#
# Data for table "students"
#

/*!40000 ALTER TABLE `students` DISABLE KEYS */;
INSERT INTO `students` VALUES (1,2,'王敬晨',2,NULL);
/*!40000 ALTER TABLE `students` ENABLE KEYS */;

#
# Structure for table "subject_groups"
#

DROP TABLE IF EXISTS `subject_groups`;
CREATE TABLE `subject_groups` (
  `group_id` int(11) NOT NULL AUTO_INCREMENT,
  `group_name` varchar(100) NOT NULL,
  `school_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`group_id`),
  KEY `school_id` (`school_id`)
) ENGINE=MyISAM AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

#
# Data for table "subject_groups"
#

/*!40000 ALTER TABLE `subject_groups` DISABLE KEYS */;
INSERT INTO `subject_groups` VALUES (1,'物理组',NULL),(2,'化学组',NULL),(3,'生物组',NULL);
/*!40000 ALTER TABLE `subject_groups` ENABLE KEYS */;

#
# Structure for table "topics"
#

DROP TABLE IF EXISTS `topics`;
CREATE TABLE `topics` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `source_id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  `author_name` varchar(100) DEFAULT NULL,
  `student_description` text,
  `easy_description` text,
  `medium_description` text,
  `difficult_description` text,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `group_id` int(11) DEFAULT NULL,
  `school_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `school_id` (`school_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

#
# Data for table "topics"
#

/*!40000 ALTER TABLE `topics` DISABLE KEYS */;
/*!40000 ALTER TABLE `topics` ENABLE KEYS */;

#
# Structure for table "users"
#

DROP TABLE IF EXISTS `users`;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `password_hash` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `is_new_user` tinyint(1) NOT NULL DEFAULT '1',
  `group_id` int(11) DEFAULT NULL,
  `role` varchar(255) COLLATE utf8_unicode_ci DEFAULT NULL,
  `school_id` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  KEY `school_id` (`school_id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

#
# Data for table "users"
#

/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (2,'王敬晨','scrypt:32768:8:1$lQZSAH0cxWx3SAgq$d4b14467ad5ddaa8434700126202502aa911fcb612f81e06bcef50c855b830fbfa80123b003ee5ea003d15e85fc73b6e03e5c0533b55ea66440441d6458c748b','2025-11-21 20:07:28',0,NULL,'teacher',NULL);
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
