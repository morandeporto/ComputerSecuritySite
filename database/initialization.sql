CREATE DATABASE IF NOT EXISTS CommunicationLTD;

USE CommunicationLTD;

CREATE TABLE sectors (
    sector_id INT AUTO_INCREMENT PRIMARY KEY,
    sector_name VARCHAR(100)
);

CREATE TABLE internet_packages (
    package_id INT AUTO_INCREMENT PRIMARY KEY,
    package_type VARCHAR(50)
);

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(200),
    email VARCHAR(100) UNIQUE,
    reset_token VARCHAR(200)
);

CREATE TABLE clients (
    client_id INT AUTO_INCREMENT PRIMARY KEY,
    representative_id INT,
    sector_id INT,
    package_id INT,
    ssn VARCHAR(11),
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    phone_number VARCHAR(20),
    FOREIGN KEY (representative_id) REFERENCES users(user_id),
    FOREIGN KEY (sector_id) REFERENCES sectors(sector_id),
    FOREIGN KEY (package_id) REFERENCES internet_packages(package_id)
);

CREATE TABLE user_sectors (
    user_id INT,
    sector_id INT,
    PRIMARY KEY (user_id, sector_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (sector_id) REFERENCES sectors(sector_id)
);

CREATE TABLE password_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    password VARCHAR(200),
    salt VARCHAR(64),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE user_info (
    user_id INT PRIMARY KEY,
    salt VARCHAR(64),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

INSERT INTO sectors (sector_name)
VALUES
('Technology & Telecommunications'),
('Science & Environment'),
('Arts & Lifestyle'),
('Education & Law'),
('Health & Sports'),
('Finance & Real Estate'),
('Entertainment & Travel'),
('Politics & Business'),
('Food & Agriculture');

INSERT INTO internet_packages (package_type)
VALUES
('Basic'),
('Standard'),
('Premium');
