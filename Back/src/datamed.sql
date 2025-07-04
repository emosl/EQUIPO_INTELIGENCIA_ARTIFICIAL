DROP DATABASE IF EXISTS datamed;
CREATE DATABASE datamed;
USE datamed;

CREATE TABLE doctors(
	id INT PRIMARY KEY NOT NULL,
    name VARCHAR(100) NOT NULL,
    father_surname VARCHAR(100) NOT NULL,
    mother_surname VARCHAR(100) NOT NULL,
    email VARCHAR(254) NOT NULL,
    password VARCHAR(50) NOT NULL,
    is_active BOOL NOT NULL
);

CREATE TABLE patients(
	id INT PRIMARY KEY NOT NULL,
    user_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    father_surname VARCHAR(100) NOT NULL,
    mother_surname VARCHAR(100) NOT NULL,
    birth_date DATE NOT NULL, -- or age?
    sex VARCHAR(1) NOT NULL
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE sessionss(
    id INT PRIMARY KEY NOT NULL,
    patient_id INT NOT NULL,
    session_timestamp TIMESTAMP NOT NULL,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id),
);

CREATE TABLE eeg_data(
    session_id INT NOT NULL,
    af3 FLOAT NOT NULL,
    f7 FLOAT NOT NULL,
    f3 FLOAT NOT NULL,
    fc5 FLOAT NOT NULL,
    t7 FLOAT NOT NULL,
    p7 FLOAT NOT NULL,
    o1 FLOAT NOT NULL,
    o2 FLOAT NOT NULL,
    p8 FLOAT NOT NULL,
    t8 FLOAT NOT NULL,
    fc6 FLOAT NOT NULL,
    f4 FLOAT NOT NULL,
    f8 FLOAT NOT NULL,
    af4 FLOAT NOT NULL,
    FOREIGN KEY (session_id) REFERENCES sessionss(session_id)
);

CREATE TABLE kalman_data(
    patient_id INT NOT NULL,
    amplitude FLOAT,
    welch FLOAT,
    FOREIGN KEY (patient_id) REFERENCES patients(patient_id)
)