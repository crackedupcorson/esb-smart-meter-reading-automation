CREATE TABLE meter_readings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reading_date DATE NOT NULL,
    import_reading FLOAT NOT NULL,
    export_reading FLOAT NOT NULL
);
CREATE USER 'meter-reader'@'localhost' IDENTIFIED WITH mysql_native_password BY 'meter-reader';
GRANT ALL PRIVILEGES ON * . * TO 'meter-reader'@'localhost';