CREATE DATABASE CommunicationLTD;
GO

USE CommunicationLTD;
GO

CREATE TABLE sectors (
    sector_id INT IDENTITY(1,1) PRIMARY KEY,
    sector_name VARCHAR(100)
);
GO

CREATE TABLE internet_packages (
    package_id INT IDENTITY(1,1) PRIMARY KEY,
    package_type VARCHAR(50)
);
GO

CREATE TABLE users (
    user_id INT IDENTITY(1,1) PRIMARY KEY,
    username VARCHAR(50),
    password VARCHAR(200),
    email VARCHAR(100),
    package_id INT,
    FOREIGN KEY (package_id) REFERENCES internet_packages(package_id),
    salt VARCHAR(64), -- Store the salt as a VARCHAR with sufficient length
);
GO

CREATE TABLE user_sectors (
    user_id INT,
    sector_id INT,
    PRIMARY KEY (user_id, sector_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (sector_id) REFERENCES sectors(sector_id)
);
GO

CREATE TABLE PasswordReset (
    email VARCHAR(100) PRIMARY KEY,
    hash_code VARCHAR(200) -- Adjust the size according to your hashing algorithm
);
GO
INSERT INTO sectors (sector_name)
VALUES
('Technology'),
('Science'),
('Arts'),
('Education'),
('Health'),
('Finance'),
('Sports'),
('Entertainment'),
('Politics'),
('Travel'),
('Fashion'),
('Food'),
('Lifestyle'),
('Business'),
('Environment'),
('Automotive'),
('Real Estate'),
('Law'),
('Agriculture'),
('Telecommunications');
GO

INSERT INTO internet_packages (package_type)
VALUES
('Basic'),
('Standard'),
('Premium');
GO

