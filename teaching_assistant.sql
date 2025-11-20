# Host: localhost  (Version: 5.7.26)
# Date: 2025-11-20 16:16:08
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
  PRIMARY KEY (`id`),
  KEY `student_id` (`student_id`),
  KEY `question_id` (`question_id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

#
# Data for table "assigned_questions"
#

/*!40000 ALTER TABLE `assigned_questions` DISABLE KEYS */;
/*!40000 ALTER TABLE `assigned_questions` ENABLE KEYS */;

#
# Structure for table "classes"
#

DROP TABLE IF EXISTS `classes`;
CREATE TABLE `classes` (
  `class_id` int(11) NOT NULL AUTO_INCREMENT,
  `class_name` varchar(50) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`class_id`)
) ENGINE=MyISAM AUTO_INCREMENT=6 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

#
# Data for table "classes"
#

/*!40000 ALTER TABLE `classes` DISABLE KEYS */;
INSERT INTO `classes` VALUES (2,'2班'),(4,'4班'),(5,'5班');
/*!40000 ALTER TABLE `classes` ENABLE KEYS */;

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
  PRIMARY KEY (`question_id`)
) ENGINE=MyISAM AUTO_INCREMENT=10 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

#
# Data for table "questions"
#

/*!40000 ALTER TABLE `questions` DISABLE KEYS */;
INSERT INTO `questions` VALUES (1,'easy','回声定位',NULL,'测试1',NULL,'测试1','2025-11-14 20:48:33'),(2,'easy','基础代数',NULL,'已知 2x + 3 = 9，求 x',NULL,'x = 3','2025-11-19 21:21:20'),(3,'medium','函数与图像',NULL,'已知 2x + 3 = 11，求 x',NULL,'x = 4','2025-11-19 21:24:48'),(4,'medium','分数四则运算',NULL,'第 1 题：请完成 分数四则运算 的练习。',NULL,'参考答案：这是第 1 题的解析。','2025-11-19 22:42:43'),(5,'medium','函数与图像',NULL,'第 2 题：请完成 函数与图像 的练习。',NULL,'参考答案：这是第 2 题的解析。','2025-11-19 22:43:53'),(6,'medium','几何思维',NULL,'第 3 题：请完成 几何思维 的练习。',NULL,'参考答案：这是第 3 题的解析。','2025-11-19 22:43:59'),(7,'difficult','概率初步',NULL,'第 4 题：请完成 概率初步 的练习。',NULL,'参考答案：这是第 4 题的解析。','2025-11-19 22:45:52'),(8,'easy','概率初步',NULL,'第 4 题：请完成 概率初步 的练习。',NULL,'参考答案：这是第 4 题的解析。','2025-11-19 22:47:20'),(9,'difficult','概率初步',NULL,'第 4 题：请完成 概率初步 的练习。',NULL,'参考答案：这是第 4 题的解析。','2025-11-19 22:55:41');
/*!40000 ALTER TABLE `questions` ENABLE KEYS */;

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
  PRIMARY KEY (`id`)
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
  PRIMARY KEY (`student_id`),
  KEY `class_id` (`class_id`)
) ENGINE=MyISAM AUTO_INCREMENT=108 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

#
# Data for table "students"
#

/*!40000 ALTER TABLE `students` DISABLE KEYS */;
INSERT INTO `students` VALUES (1,2,'高子骞'),(2,2,'胡御涛'),(3,2,'张铃'),(4,2,'罗宇涵'),(5,2,'陈昱衡'),(6,2,'李彦诚'),(7,2,'黄子毅'),(8,2,'赵伊诺'),(9,2,'吕承涵'),(10,2,'代昊龙'),(11,2,'陈伟辰'),(12,2,'夏昱澄'),(13,2,'杨浩宇'),(14,2,'罗皓然'),(15,2,'卞祖昊'),(16,2,'杨欣怡'),(17,2,'余梓涵'),(18,2,'向怡霏'),(19,2,'靳元雨'),(20,2,'任浩扬'),(21,2,'彭思涵'),(22,2,'郑瑜浩'),(23,2,'朱玉喆'),(24,2,'刘嘉芃'),(25,2,'李洲洋'),(26,2,'舒智飞'),(27,2,'王彦泽'),(28,2,'李馥吟'),(29,2,'赵泽浩'),(30,2,'刘天昊'),(31,2,'张瑾然'),(32,2,'胡暄源'),(33,2,'汪子皓'),(34,2,'周雨龙'),(35,2,'方彬翰'),(36,2,'杨思淇'),(37,2,'王思雅'),(38,2,'余晨萱'),(39,2,'汪书涵'),(40,2,'陈儒鑫'),(41,2,'李丽欣'),(42,2,'王一伊'),(43,2,'杨涵麟'),(44,5,'张峰瑞'),(45,5,'徐浩然'),(46,5,'赵禄浩'),(47,5,'魏皓轩'),(48,5,'陈嘉浩'),(49,5,'贾俊伟'),(50,5,'刘晋鹏'),(51,5,'王家毅'),(52,5,'铎浩轩'),(53,5,'代雨冉'),(54,5,'李雅雯'),(55,5,'王小文'),(56,5,'陈筱蕊'),(57,5,'程钰淇'),(58,5,'卫婼兮'),(59,5,'李与冉'),(60,5,'刘丽泽'),(61,5,'彭婷娜'),(62,5,'曹玉松'),(63,5,'熊浩棋'),(64,5,'曾鑫'),(65,5,'徐嘉诚'),(66,5,'赵俊懿'),(67,5,'涂汯熠'),(68,5,'贺隆毅'),(69,5,'牟天佑'),(70,5,'田婧希'),(71,5,'杨双忆'),(72,5,'王莉皎'),(73,5,'蔡瑞涵'),(74,5,'熊紫荷'),(75,5,'赵子涵'),(76,5,'姜星宇'),(77,5,'陈雨涵'),(78,5,'张熙坪'),(79,5,'山子涵'),(80,5,'杨雪峰'),(81,4,'袁民东'),(82,4,'邓嘉淇'),(83,4,'廖晋逸'),(84,4,'陈义卓'),(85,4,'严浩宇'),(86,4,'王子涛'),(87,4,'曾垒'),(88,4,'卫诗琪'),(89,4,'成栖鈅'),(90,4,'李婕煜'),(91,4,'李依瑞洋'),(92,4,'陈欣愉'),(93,4,'寇子曰'),(94,4,'高以达'),(95,4,'魏中俊'),(96,4,'卢宇杰'),(97,4,'钟琪鸿'),(98,4,'王浩洋'),(99,4,'周泽宇'),(100,4,'沈鑫'),(101,4,'侯云浩'),(102,4,'张汇旻'),(103,4,'李瑜薇'),(104,4,'黄诗睿'),(105,4,'殷晨曦'),(106,4,'刘邦鸿'),(107,4,'张钰玥');
/*!40000 ALTER TABLE `students` ENABLE KEYS */;

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
  PRIMARY KEY (`id`)
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
  `password` varchar(255) COLLATE utf8_unicode_ci NOT NULL,
  `role` enum('admin','teacher','assistant') COLLATE utf8_unicode_ci DEFAULT 'teacher',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

#
# Data for table "users"
#

/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'王敬晨','888888','teacher','2025-05-19 04:03:52');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
