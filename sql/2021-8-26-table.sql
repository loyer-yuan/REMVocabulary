/*
 Navicat Premium Data Transfer

 Source Server         : programDesign
 Source Server Type    : MySQL
 Source Server Version : 80020
 Source Host           : localhost:3306
 Source Schema         : remvocabulary_dbms

 Target Server Type    : MySQL
 Target Server Version : 80020
 File Encoding         : 65001

 Date: 26/08/2021 21:39:52
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for check_in_form
-- ----------------------------
DROP TABLE IF EXISTS `check_in_form`;
CREATE TABLE `check_in_form`  (
  `id` int UNSIGNED NOT NULL,
  `username` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `consecutive_check` int NOT NULL DEFAULT 0,
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`username`, `id`) USING BTREE,
  CONSTRAINT `check_in_form_ibfk_1` FOREIGN KEY (`username`) REFERENCES `user` (`username`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for example
-- ----------------------------
DROP TABLE IF EXISTS `example`;
CREATE TABLE `example`  (
  `example` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `words` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `chinese` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`example`, `words`) USING BTREE,
  INDEX `example_index`(`words`, `example`) USING BTREE,
  CONSTRAINT `example_ibfk_1` FOREIGN KEY (`words`) REFERENCES `vocabulary` (`words`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for oblivion
-- ----------------------------
DROP TABLE IF EXISTS `oblivion`;
CREATE TABLE `oblivion`  (
  `username` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `forget_number` int UNSIGNED NOT NULL DEFAULT 0,
  `remember_number` int UNSIGNED NOT NULL DEFAULT 0,
  PRIMARY KEY (`username`) USING BTREE,
  INDEX `username`(`username`) USING BTREE,
  CONSTRAINT `oblivion_ibfk_1` FOREIGN KEY (`username`) REFERENCES `user` (`username`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for oblivion_rate
-- ----------------------------
DROP TABLE IF EXISTS `oblivion_rate`;
CREATE TABLE `oblivion_rate`  (
  `username` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `date` datetime NOT NULL ON UPDATE CURRENT_TIMESTAMP,
  `rate` double NULL DEFAULT NULL,
  PRIMARY KEY (`username`, `date`) USING BTREE,
  CONSTRAINT `oblivion_rate_ibfk_1` FOREIGN KEY (`username`) REFERENCES `user` (`username`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for pronounce
-- ----------------------------
DROP TABLE IF EXISTS `pronounce`;
CREATE TABLE `pronounce`  (
  `words` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `pronounce` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `url` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NULL DEFAULT NULL,
  PRIMARY KEY (`words`, `pronounce`) USING BTREE,
  INDEX `words`(`words`, `pronounce`) USING BTREE,
  CONSTRAINT `pronounce_ibfk_1` FOREIGN KEY (`words`) REFERENCES `vocabulary` (`words`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for remember_word
-- ----------------------------
DROP TABLE IF EXISTS `remember_word`;
CREATE TABLE `remember_word`  (
  `username` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `plan_number` int UNSIGNED NULL DEFAULT 0,
  `study_number` int UNSIGNED NULL DEFAULT 0,
  `preview_number` int UNSIGNED NULL DEFAULT 0,
  PRIMARY KEY (`username`) USING BTREE,
  INDEX `username_index`(`username`) USING BTREE,
  CONSTRAINT `remember_word_ibfk_1` FOREIGN KEY (`username`) REFERENCES `user` (`username`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for temp_book
-- ----------------------------
DROP TABLE IF EXISTS `temp_book`;
CREATE TABLE `temp_book`  (
  `word` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `word-book` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `username` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  PRIMARY KEY (`word`, `word-book`, `username`) USING BTREE,
  CONSTRAINT `temp_book_ibfk_1` FOREIGN KEY (`word`, `word-book`, `username`) REFERENCES `word_book` (`words`, `word-book`, `username`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user`  (
  `username` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `alias` varchar(12) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `password` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `register_time` datetime NULL DEFAULT CURRENT_TIMESTAMP,
  `update_time` datetime NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`username`) USING BTREE,
  INDEX `username_index`(`username`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for vocabulary
-- ----------------------------
DROP TABLE IF EXISTS `vocabulary`;
CREATE TABLE `vocabulary`  (
  `words` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `part_of_speech` varchar(10) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `chinese` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  PRIMARY KEY (`words`, `part_of_speech`) USING BTREE,
  INDEX `vocabulary_index`(`words`) USING BTREE
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Table structure for word_book
-- ----------------------------
DROP TABLE IF EXISTS `word_book`;
CREATE TABLE `word_book`  (
  `words` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `word-book` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `username` varchar(32) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `degree` varchar(255) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL DEFAULT 'not_leanring',
  `time` datetime NOT NULL ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`words`, `word-book`, `username`) USING BTREE,
  INDEX `words`(`words`, `word-book`, `username`) USING BTREE,
  INDEX `username`(`username`) USING BTREE,
  CONSTRAINT `word_book_ibfk_1` FOREIGN KEY (`words`) REFERENCES `vocabulary` (`words`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `word_book_ibfk_2` FOREIGN KEY (`username`) REFERENCES `user` (`username`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

SET FOREIGN_KEY_CHECKS = 1;
