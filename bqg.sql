/*
Navicat MySQL Data Transfer

Source Server         : MT
Source Server Version : 50553
Source Host           : localhost:3306
Source Database       : bqg

Target Server Type    : MYSQL
Target Server Version : 50553
File Encoding         : 65001

Date: 2019-06-29 20:05:03
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for books
-- ----------------------------
DROP TABLE IF EXISTS `books`;
CREATE TABLE `books` (
  `book_id` int(11) NOT NULL,
  `book_name` varchar(30) DEFAULT NULL,
  `author` varchar(15) DEFAULT NULL,
  `state` varchar(20) DEFAULT NULL,
  `update_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `intro` varchar(300) DEFAULT NULL,
  PRIMARY KEY (`book_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for chapters
-- ----------------------------
DROP TABLE IF EXISTS `chapters`;
CREATE TABLE `chapters` (
  `chapter_id` int(11) NOT NULL,
  `book_id` int(11) DEFAULT NULL,
  `title` varchar(50) DEFAULT NULL,
  `state` tinyint(4) DEFAULT '0',
  `content` text,
  PRIMARY KEY (`chapter_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
