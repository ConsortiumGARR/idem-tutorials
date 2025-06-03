SET NAMES 'utf8';

SET CHARACTER SET utf8;

CREATE DATABASE IF NOT EXISTS shibpid CHARACTER SET=utf8;

GRANT ALL PRIVILEGES ON shibpid.* TO 'root'@'localhost';

-- ##_SHIBPID-DB_USER-PASSWORD-CHANGEME_## can't contain the characters:  ;   &   #   <
CREATE USER IF NOT EXISTS '###_SHIBPID-USERNAME-CHANGEME_###'@'localhost' IDENTIFIED BY '###_SHIBPID-DB-USER-PASSWORD-CHANGEME_###';
GRANT ALL PRIVILEGES ON shibpid.* TO '###_SHIBPID-USERNAME-CHANGEME_###'@'localhost';

FLUSH PRIVILEGES;

USE shibpid;

CREATE TABLE IF NOT EXISTS shibpid
(
   localEntity VARCHAR(1024) NOT NULL COLLATE utf8_bin,
   peerEntity VARCHAR(1024) NOT NULL COLLATE utf8_bin,
   persistentId VARCHAR(50) NOT NULL COLLATE utf8_bin,
   principalName VARCHAR(255) NOT NULL,
   localId VARCHAR(255) NOT NULL,
   peerProvidedId VARCHAR(255) NULL,
   creationDate TIMESTAMP NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
   deactivationDate TIMESTAMP NULL default NULL,
   PRIMARY KEY (localEntity(255), peerEntity(255), persistentId(50))
);

quit
