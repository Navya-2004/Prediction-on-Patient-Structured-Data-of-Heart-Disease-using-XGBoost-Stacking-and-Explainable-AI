drop database if exists  HeartDisease;
create database HeartDisease;
use HeartDisease;

create table users (
    id INT PRIMARY KEY AUTO_INCREMENT, 
    name VARCHAR(225),
    email VARCHAR(50), 
    password VARCHAR(50)
    );
