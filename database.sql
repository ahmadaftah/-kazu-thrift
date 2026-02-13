-- Create Database
CREATE DATABASE IF NOT EXISTS thrift_db;
USE thrift_db;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role ENUM('Admin', 'Staff') DEFAULT 'Staff'
);

-- Inventory Table
CREATE TABLE IF NOT EXISTS inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50),
    price DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL,
    item_condition ENUM('Baru', 'Seperti Baru', 'Bagus', 'Layak Pakai') DEFAULT 'Bagus',
    image_url VARCHAR(255) DEFAULT 'default-product.png',
    entry_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sales Table (for Visualization)
CREATE TABLE IF NOT EXISTS sales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT,
    quantity INT NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES inventory(id) ON DELETE CASCADE
);

-- Insert Dummy Users with Roles
INSERT IGNORE INTO users (username, password, full_name, role) VALUES 
('admin', 'admin123', 'Administrator Thrift', 'Admin'),
('staff', 'staff123', 'Staff Toko', 'Staff');

-- Insert Dummy Inventory
INSERT IGNORE INTO inventory (name, category, price, stock, item_condition) VALUES 
('Jaket Vintage Nike', 'Pakaian Luar', 250000, 5, 'Seperti Baru'),
('Celana Levi\'s 501', 'Bawahan', 150000, 10, 'Bagus'),
('Kaos Oversize Uniqlo', 'Atasan', 75000, 20, 'Baru'),
('Sepatu Converse 70s', 'Alas Kaki', 350000, 3, 'Bagus');

-- Insert Dummy Sales for Chart
INSERT IGNORE INTO sales (product_id, quantity, total_price, sale_date) VALUES 
(1, 1, 250000, '2026-02-10 10:00:00'),
(2, 2, 300000, '2026-02-11 11:30:00'),
(3, 5, 375000, '2026-02-12 09:15:00'),
(1, 1, 250000, '2026-02-13 14:00:00');
