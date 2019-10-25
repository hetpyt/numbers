-- phpMyAdmin SQL Dump
-- version 4.4.15.10
-- https://www.phpmyadmin.net
--
-- Хост: localhost
-- Время создания: Окт 25 2019 г., 11:47
-- Версия сервера: 10.0.36-MariaDB
-- Версия PHP: 5.4.16

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- База данных: `moop`
--
CREATE DATABASE IF NOT EXISTS `moop` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
USE `moop`;

-- --------------------------------------------------------

--
-- Структура таблицы `clients`
--

DROP TABLE IF EXISTS `clients`;
CREATE TABLE IF NOT EXISTS `clients` (
  `id` int(10) unsigned NOT NULL,
  `account` varchar(15) NOT NULL,
  `phone_number` varchar(12) NOT NULL,
  `registration_date` datetime NOT NULL DEFAULT '0000-00-00 00:00:00'
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8;

--
-- Дамп данных таблицы `clients`
--

INSERT INTO `clients` (`id`, `account`, `phone_number`, `registration_date`) VALUES
(1, '123456', '+79115792506', '2019-06-25 14:18:00'),
(4, '654321', '+79115556677', '2019-06-25 14:45:15'),
(5, '0000045858', '+79115792506', '2019-10-21 10:58:52');

-- --------------------------------------------------------

--
-- Структура таблицы `meters`
--

DROP TABLE IF EXISTS `meters`;
CREATE TABLE IF NOT EXISTS `meters` (
  `id` int(10) unsigned NOT NULL,
  `owner_id` int(10) unsigned NOT NULL,
  `index_num` int(3) NOT NULL COMMENT 'порядковый номер счетчика в учетной системе',
  `updated_from_db` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `count_from_db` float(10,5) NOT NULL,
  `count` float(10,5) NOT NULL
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

--
-- Дамп данных таблицы `meters`
--

INSERT INTO `meters` (`id`, `owner_id`, `index_num`, `updated_from_db`, `updated`, `count_from_db`, `count`) VALUES
(2, 5, 1, '2019-10-25 11:43:33', '2019-10-25 11:43:33', 101.00000, 0.00000),
(3, 5, 2, '2019-10-25 11:43:42', '2019-10-25 11:43:42', 202.00000, 0.00000);

-- --------------------------------------------------------

--
-- Структура таблицы `pers_set`
--

DROP TABLE IF EXISTS `pers_set`;
CREATE TABLE IF NOT EXISTS `pers_set` (
  `phone_number` varchar(12) NOT NULL,
  `greeting_f` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Дамп данных таблицы `pers_set`
--

INSERT INTO `pers_set` (`phone_number`, `greeting_f`) VALUES
('+79115792506', 'gr_9115792506');

--
-- Индексы сохранённых таблиц
--

--
-- Индексы таблицы `clients`
--
ALTER TABLE `clients`
  ADD PRIMARY KEY (`id`) USING BTREE,
  ADD KEY `phone_number` (`phone_number`);

--
-- Индексы таблицы `meters`
--
ALTER TABLE `meters`
  ADD PRIMARY KEY (`id`),
  ADD KEY `owner_id` (`owner_id`);

--
-- Индексы таблицы `pers_set`
--
ALTER TABLE `pers_set`
  ADD PRIMARY KEY (`phone_number`) USING BTREE;

--
-- AUTO_INCREMENT для сохранённых таблиц
--

--
-- AUTO_INCREMENT для таблицы `clients`
--
ALTER TABLE `clients`
  MODIFY `id` int(10) unsigned NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=6;
--
-- AUTO_INCREMENT для таблицы `meters`
--
ALTER TABLE `meters`
  MODIFY `id` int(10) unsigned NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=4;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
