CREATE DATABASE IF NOT EXISTS crypto;
USE crypto;
CREATE TABLE IF NOT EXISTS bitcoin_rates (
    iteration_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    time_stamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    current_rate FLOAT,
    avarage_rate FLOAT );