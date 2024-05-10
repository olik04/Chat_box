DROP DATABASE IF EXISTS chats;

CREATE DATABASE chats;

CREATE TABLE `chats`.`users` (
    `user_id` INT AUTO_INCREMENT NOT NULL,
    `username` VARCHAR(30) NOT NULL,
    `password` VARCHAR(30) NOT NULL,
    PRIMARY KEY (`user_id`)
);

CREATE TABLE `chats`.`chats` (
    `chat_id` INT AUTO_INCREMENT NOT NULL,
    `chat_type` TINYINT NOT NULL,
    `chat_name` VARCHAR(255) NOT NULL,
    PRIMARY KEY (`chat_id`)
);

CREATE TABLE `chats`.`messages` (
    `msg_id` INT AUTO_INCREMENT NOT NULL,
    `msg_text` VARCHAR(255) NOT NULL,
    `user_id` INT NOT NULL,
    `chat_id` INT NOT NULL,
    `sent_time` TIMESTAMP NOT NULL,
    PRIMARY KEY (`msg_id`),
    FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`),
    FOREIGN KEY (`chat_id`) REFERENCES `chats`(`chat_id`)
);

CREATE TABLE `chats`.`chat_user` (
    `chat_id` INT NOT NULL,
    `user_id` INT NOT NULL,
    `added_time` TIMESTAMP NOT NULL,
    `removed_time` TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`),
    FOREIGN KEY (`chat_id`) REFERENCES `chats`(`chat_id`)
);

INSERT INTO `chats`.`users` (`username`, `password`) VALUES ('alikhan', 'password');

