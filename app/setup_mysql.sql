-- Script that prepares A MySQL server for the project
-- create a database if not exists 'hrm_db'
-- create a new user if not exists 'hrm_user' in localhost with password hrm_password
-- And hrm_user have all privileges on the database hrm_db
-- And hrm_user have 'SELECT' provilages on the database performance_schema
CREATE DATABASE IF NOT EXISTS hrm_db;
CREATE USER IF NOT EXISTS 'hrm_user'@'localhost' IDENTIFIED BY 'hrm_password';
GRANT ALL PRIVILEGES ON hrm_db.* TO 'hrm_user'@'localhost';
GRANT SELECT ON performance_schema.* TO 'hrm_user'@'localhost';
FLUSH PRIVILEGES;