-- =============================================
-- Создание базы данных
-- =============================================
CREATE DATABASE IF NOT EXISTS shipping_db;
USE shipping_db;

-- =============================================
-- Таблица пользователей
-- =============================================
CREATE TABLE IF NOT EXISTS users (
    id INT(11) AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin','user') NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    phone VARCHAR(20),
    email VARCHAR(100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Таблица стран
-- =============================================
CREATE TABLE IF NOT EXISTS countries (
    country_id INT AUTO_INCREMENT PRIMARY KEY,
    country_name VARCHAR(50) NOT NULL UNIQUE,
    default_transport_type ENUM('морем','наземный','комбинированный') NOT NULL,
    main_port VARCHAR(100),
    avg_shipping_days INT CHECK (avg_shipping_days >= 0),
    customs_notes TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Таблица статусов доставки
-- =============================================
CREATE TABLE IF NOT EXISTS delivery_status (
    status_id INT AUTO_INCREMENT PRIMARY KEY,
    status_name VARCHAR(50) NOT NULL UNIQUE,
    order_index INT NOT NULL,
    icon VARCHAR(100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Таблица покупок
-- =============================================
CREATE TABLE IF NOT EXISTS purchases (
    purchase_id INT AUTO_INCREMENT PRIMARY KEY,
    vin_number VARCHAR(50) NOT NULL,
    car_make VARCHAR(50) NOT NULL,
    car_model VARCHAR(50) NOT NULL,
    car_year YEAR NOT NULL,
    buyer_id INT NOT NULL,
    country_id INT NOT NULL,
    purchase_date DATE NOT NULL,
    price_usd DECIMAL(10,2) NOT NULL CHECK (price_usd >= 0),
    delivery_status_id INT NOT NULL,
    estimated_arrival_date DATE,
    is_delivered BOOLEAN DEFAULT FALSE,
    auction_name VARCHAR(100),
    current_city VARCHAR(100),
    notes TEXT,
    FOREIGN KEY (buyer_id) REFERENCES users(id),
    FOREIGN KEY (country_id) REFERENCES countries(country_id),
    FOREIGN KEY (delivery_status_id) REFERENCES delivery_status(status_id),
    CONSTRAINT chk_estimated_date CHECK (estimated_arrival_date IS NULL OR estimated_arrival_date >= purchase_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Таблица точек маршрута
-- =============================================
CREATE TABLE IF NOT EXISTS delivery_route_points (
    point_id INT AUTO_INCREMENT PRIMARY KEY,
    purchase_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    latitude DECIMAL(9,6) NOT NULL CHECK (latitude BETWEEN -90 AND 90),
    longitude DECIMAL(9,6) NOT NULL CHECK (longitude BETWEEN -180 AND 180),
    arrival_date DATE,
    departure_date DATE,
    transport_mode ENUM('морем','поезд','грузовик') NOT NULL,
    status_id INT NOT NULL,
    notes TEXT,
    FOREIGN KEY (purchase_id) REFERENCES purchases(purchase_id) ON DELETE CASCADE,
    FOREIGN KEY (status_id) REFERENCES delivery_status(status_id),
    CONSTRAINT uq_route_point UNIQUE (purchase_id, name, arrival_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Таблица фотографий авто
-- =============================================
CREATE TABLE IF NOT EXISTS purchase_images (
    image_id INT AUTO_INCREMENT PRIMARY KEY,
    purchase_id INT NOT NULL,
    point_id INT,
    image_url VARCHAR(255) NOT NULL,
    image_type ENUM('auction','port','in_transit','other') NOT NULL,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (purchase_id) REFERENCES purchases(purchase_id) ON DELETE CASCADE,
    FOREIGN KEY (point_id) REFERENCES delivery_route_points(point_id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- =============================================
-- Таблица транспортных компаний
-- =============================================
CREATE TABLE IF NOT EXISTS shipping_companies (
    shipping_company_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    country_id INT NOT NULL,
    contact_info VARCHAR(255),
    rating DECIMAL(3,2) CHECK (rating >= 0 AND rating <= 5),
    website VARCHAR(255),
    FOREIGN KEY (country_id) REFERENCES countries(country_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
