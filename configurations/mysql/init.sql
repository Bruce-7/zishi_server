-- 设置数据库字符集和排序规则
SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建应用数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS `${MYSQL_DATABASE}` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 授予权限
GRANT ALL PRIVILEGES ON `${MYSQL_DATABASE}`.* TO 'root'@'%' IDENTIFIED BY '${MYSQL_ROOT_PASSWORD}';
FLUSH PRIVILEGES;

-- 使用数据库
USE `${MYSQL_DATABASE}`;

-- 设置时区
SET time_zone = '+08:00';

-- 设置SQL模式
SET GLOBAL sql_mode = 'STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- 设置连接超时和等待超时
SET GLOBAL connect_timeout = 28800;
SET GLOBAL wait_timeout = 28800;
SET GLOBAL interactive_timeout = 28800;
