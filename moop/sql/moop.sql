SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;


CREATE TABLE IF NOT EXISTS `clients` (
  `id` int(10) unsigned NOT NULL,
  `account` varchar(15) NOT NULL,
  `phone_number` varchar(12) NOT NULL,
  `registration_date` datetime NOT NULL DEFAULT '0000-00-00 00:00:00'
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `meters` (
  `id` int(10) unsigned NOT NULL,
  `owner_id` int(10) unsigned NOT NULL,
  `index_num` int(3) NOT NULL COMMENT 'порядковый номер счетчика в учетной системе',
  `updated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `count` float(10,5) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `meters_readings` (
  `id` int(10) unsigned NOT NULL,
  `meter_id` int(10) NOT NULL,
  `count` float(10,5) NOT NULL,
  `updated` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT='таблица для хранения переданных показаний';

CREATE TABLE IF NOT EXISTS `pers_set` (
  `phone_number` varchar(12) NOT NULL,
  `greeting_f` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


ALTER TABLE `clients`
  ADD PRIMARY KEY (`id`) USING BTREE,
  ADD KEY `phone_number` (`phone_number`);

ALTER TABLE `meters`
  ADD PRIMARY KEY (`id`),
  ADD KEY `owner_id` (`owner_id`);

ALTER TABLE `meters_readings`
  ADD PRIMARY KEY (`id`) USING BTREE,
  ADD KEY `meter_id` (`meter_id`) USING BTREE;

ALTER TABLE `pers_set`
  ADD PRIMARY KEY (`phone_number`) USING BTREE;


ALTER TABLE `clients`
  MODIFY `id` int(10) unsigned NOT NULL AUTO_INCREMENT;
ALTER TABLE `meters`
  MODIFY `id` int(10) unsigned NOT NULL AUTO_INCREMENT;
ALTER TABLE `meters_readings`
  MODIFY `id` int(10) unsigned NOT NULL AUTO_INCREMENT;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
