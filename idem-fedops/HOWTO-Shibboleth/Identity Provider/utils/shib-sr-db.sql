SET NAMES 'utf8';

SET CHARACTER SET utf8;

CREATE DATABASE IF NOT EXISTS storagerecords CHARACTER SET=utf8;

GRANT ALL PRIVILEGES ON storagerecords.* TO 'root'@'localhost';

-- ##_SR-DB_USER-PASSWORD-CHANGEME_## can't contain the characters:  ;   &   #   <
CREATE USER IF NOT EXISTS '###_SR-USERNAME-CHANGEME_###'@'localhost' IDENTIFIED BY '###_SR-DB-USER-PASSWORD-CHANGEME_###';
GRANT ALL PRIVILEGES ON storagerecords.* TO '###_SR-USERNAME-CHANGEME_###'@'localhost';

FLUSH PRIVILEGES;

USE storagerecords;

CREATE TABLE IF NOT EXISTS StorageRecords
(
context VARCHAR(255) NOT NULL COLLATE utf8_bin,
id VARCHAR(255) NOT NULL COLLATE utf8_bin,
expires BIGINT(20) DEFAULT NULL,
value LONGTEXT NOT NULL,
version BIGINT(20) NOT NULL,
PRIMARY KEY (context, id)
);

quit
