-- Creación de base de datos
CREATE DATABASE IF NOT EXISTS MedicamentosDB;
USE MedicamentosDB;

-- Tabla: Medicamento
CREATE TABLE Medicamento (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    time TIME NOT NULL,
    grams INT NOT NULL CHECK (grams > 0),
    days INT NOT NULL CHECK (days > 0),
    hours INT NOT NULL CHECK (hours > 0),
    total_doses INT NOT NULL CHECK (total_doses >= 0),
    taken_doses INT NOT NULL DEFAULT 0 CHECK (taken_doses >= 0),
    completed BOOLEAN NOT NULL DEFAULT FALSE,
    start_date DATE NOT NULL,
    current_alert_time TIME NOT NULL,
    last_notification_time TIME NULL
);