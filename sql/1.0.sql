-- phpMyAdmin SQL Dump
-- version 4.8.5
-- https://www.phpmyadmin.net/
--
-- 主机： localhost
-- 生成日期： 2023-10-09 03:03:11
-- 服务器版本： 5.7.26
-- PHP 版本： 7.3.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 数据库： `check`
--

-- --------------------------------------------------------

--
-- 表的结构 `devopen_users`
--

CREATE TABLE `devopen_users` (
  `ID` int(11) NOT NULL,
  `FanbookUserId` varchar(255) NOT NULL,
  `FanbookID` varchar(255) NOT NULL,
  `nickname` varchar(255) NOT NULL,
  `today` varchar(255) NOT NULL,
  `total` varchar(255) NOT NULL,
  `money` varchar(255) NOT NULL,
  `img_pay` varchar(25) DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

--
-- 转存表中的数据 `devopen_users`
--

INSERT INTO `devopen_users` (`ID`, `FanbookUserId`, `FanbookID`, `nickname`, `today`, `total`, `money`, `img_pay`) VALUES
(10001, '375274330516357120', '6897520', '汪嗯个凉-晚六晚十', '20231009', '8', '0.0', 'https://fanbook.mobi');

--
-- 转储表的索引
--

--
-- 表的索引 `devopen_users`
--
ALTER TABLE `devopen_users`
  ADD PRIMARY KEY (`ID`);

--
-- 在导出的表使用AUTO_INCREMENT
--

--
-- 使用表AUTO_INCREMENT `devopen_users`
--
ALTER TABLE `devopen_users`
  MODIFY `ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10002;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
