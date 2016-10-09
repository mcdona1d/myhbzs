/*
Navicat MySQL Data Transfer

Source Server         : QCloud_admin
Source Server Version : 50173
Source Host           : 127.0.0.1:3306
Source Database       : wechat_platform

Target Server Type    : MYSQL
Target Server Version : 50173
File Encoding         : 65001

Date: 2016-06-07 17:45:42
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for collect
-- ----------------------------
DROP TABLE IF EXISTS `collect`;
CREATE TABLE `collect` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `openid` varchar(255) NOT NULL,
  `bookid` varchar(255) NOT NULL,
  `collect` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `collect-cascade` (`openid`),
  CONSTRAINT `collect-cascade` FOREIGN KEY (`openid`) REFERENCES `user` (`openid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=25 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for exam
-- ----------------------------
DROP TABLE IF EXISTS `exam`;
CREATE TABLE `exam` (
  `openid` varchar(255) CHARACTER SET utf8 NOT NULL COMMENT '用户唯一标识',
  `exam` text CHARACTER SET utf8 COMMENT '考试安排内容',
  PRIMARY KEY (`openid`),
  CONSTRAINT `exam-cascade` FOREIGN KEY (`openid`) REFERENCES `user` (`openid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- ----------------------------
-- Table structure for schedule
-- ----------------------------
DROP TABLE IF EXISTS `schedule`;
CREATE TABLE `schedule` (
  `openid` varchar(255) CHARACTER SET utf8 NOT NULL COMMENT '用户唯一标识',
  `schedule` text CHARACTER SET utf8 COMMENT '课程表内容',
  `modify` text,
  PRIMARY KEY (`openid`),
  CONSTRAINT `schedule-cascade` FOREIGN KEY (`openid`) REFERENCES `user` (`openid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- ----------------------------
-- Table structure for score
-- ----------------------------
DROP TABLE IF EXISTS `score`;
CREATE TABLE `score` (
  `openid` varchar(255) CHARACTER SET utf8 NOT NULL COMMENT '用户唯一标识',
  `score` text CHARACTER SET utf8 COMMENT '学期成绩内容',
  PRIMARY KEY (`openid`),
  CONSTRAINT `score-cascade` FOREIGN KEY (`openid`) REFERENCES `user` (`openid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `openid` varchar(30) CHARACTER SET utf8 NOT NULL COMMENT '用户唯一标识',
  `value` varchar(16) CHARACTER SET utf8 NOT NULL COMMENT '用户随机字符串',
  `jw_id` varchar(8) CHARACTER SET utf8 NOT NULL COMMENT '正方账号 学号',
  `jw_pass` varchar(16) CHARACTER SET utf8 NOT NULL COMMENT '正方账号 密码',
  PRIMARY KEY (`openid`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
