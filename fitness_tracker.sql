CREATE DATABASE fitness_tracker;

USE fitness_tracker;

-- members table - Customer table from ecommerce

CREATE TABLE Members (
	member_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150),
    phone_number VARCHAR(150),
    credit_card VARCHAR(30)
);

-- Workout session table - orders
CREATE TABLE Workouts (
	workout_id INT AUTO_INCREMENT PRIMARY KEY,
	activity VARCHAR(150) NOT NULL,
    date DATE,
    time TIME,
    member_id INT,
    FOREIGN KEY(member_id) REFERENCES Members(member_id)
);

INSERT INTO Members (name, email, phone_number, credit_card)
VALUES ("Obi Wan Kenobi", "oleben@gmail.com", "63085475", "8465189894616338");

INSERT INTO Workouts (activity, date, member_id)
VALUES ("cardio", "2024-05-29", "1");

ALTER TABLE Workouts DROP COLUMN time;

SELECT *
FROM Members;
-- date format "yyyy-mm-dd"
-- time format "hh:mm:ss"