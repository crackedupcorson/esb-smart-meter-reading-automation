CREATE TABLE meter_readings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reading_date DATE NOT NULL,
    mprn VARCHAR(32) NOT NULL
);