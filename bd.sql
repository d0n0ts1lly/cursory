-- ---------------------------------------------------------
-- Дамп бази даних shipping_db
-- ---------------------------------------------------------

CREATE DATABASE IF NOT EXISTS shipping_db
  DEFAULT CHARACTER SET utf8mb4
  COLLATE utf8mb4_general_ci;
USE shipping_db;

-- ---------------------------------------------------------
-- Таблиця users
-- ---------------------------------------------------------
DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin','user') NOT NULL DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    phone VARCHAR(20),
    email VARCHAR(100)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO users (id, username, password_hash, role, phone, email, created_at) VALUES
(1, 'ivan',  '$2y$10$sd879sdf78sd6f8sd678sd6fd', 'user',  '+380671234567', 'ivan@example.com',  '2025-11-20 10:00:00'),
(2, 'admin', '$2y$10$as91asd9as8d7as6d87asd9as', 'admin', '+380501112233', 'admin@example.com', '2025-10-01 09:15:00');

-- ---------------------------------------------------------
-- Таблиця countries
-- ---------------------------------------------------------
DROP TABLE IF EXISTS countries;
CREATE TABLE countries (
    country_id INT AUTO_INCREMENT PRIMARY KEY,
    country_name VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO countries (country_id, country_name) VALUES
(1, 'Сполучені Штати Америки'),
(2, 'Японія'),
(3, 'Німеччина'),
(4, 'Китай'),
(5, 'Литва'),
(6, 'Польща');

-- ---------------------------------------------------------
-- Таблиця ports
-- ---------------------------------------------------------
DROP TABLE IF EXISTS ports;
CREATE TABLE ports (
    port_id INT AUTO_INCREMENT PRIMARY KEY,
    port_name VARCHAR(100) NOT NULL,
    country_id INT NOT NULL,
    delivery_to_europe_days INT NOT NULL,
    FOREIGN KEY (country_id) REFERENCES countries(country_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO ports (port_id, port_name, country_id, delivery_to_europe_days) VALUES
(1, 'Baltimore', 1, 14),
(2, 'Yokohama', 2, 16),
(3, 'Hamburg',   3, 2),
(4, 'Shanghai',  4, 20),
(5, 'Klaipėda',  5, 0),
(6, 'Gdynia',    6, 1);

-- ---------------------------------------------------------
-- Таблиця auctions
-- ---------------------------------------------------------
DROP TABLE IF EXISTS auctions;
CREATE TABLE auctions (
    auction_id INT AUTO_INCREMENT PRIMARY KEY,
    auction_name VARCHAR(100) NOT NULL,
    country_id INT NOT NULL,
    FOREIGN KEY (country_id) REFERENCES countries(country_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO auctions (auction_id, auction_name, country_id) VALUES
(1, 'Copart USA', 1),
(2, 'IAAI USA', 1),
(3, 'USS Japan', 2),
(4, 'Autorola Germany', 3),
(5, 'Copart China', 4),
(6, 'Baltic Auctions LT', 5);

-- ---------------------------------------------------------
-- Таблиця locations
-- ---------------------------------------------------------
DROP TABLE IF EXISTS locations;
CREATE TABLE locations (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    location_name VARCHAR(100) NOT NULL,
    country_id INT NOT NULL,
    default_port_id INT NOT NULL,
    days_to_port INT NOT NULL,
    FOREIGN KEY (country_id) REFERENCES countries(country_id),
    FOREIGN KEY (default_port_id) REFERENCES ports(port_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO locations (location_id, location_name, country_id, default_port_id, days_to_port) VALUES
(1, 'Маямі (США)',        1, 1, 3),
(2, 'Лос-Анджелес (США)', 1, 1, 5),
(3, 'Токіо (Японія)',     2, 2, 1),
(4, 'Берлін (Німеччина)', 3, 3, 1),
(5, 'Шанхай (Китай)',     4, 4, 2),
(6, 'Вільнюс (Литва)',    5, 5, 1),
(7, 'Варшава (Польща)',   6, 6, 1);

-- ---------------------------------------------------------
-- Таблиця statuses
-- ---------------------------------------------------------
DROP TABLE IF EXISTS statuses;
CREATE TABLE statuses (
    status_id INT AUTO_INCREMENT PRIMARY KEY,
    status_key VARCHAR(50) NOT NULL UNIQUE,
    status_name VARCHAR(100) NOT NULL,
    order_index INT NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO statuses (status_id, status_key, status_name, order_index) VALUES
(1, 'bought_auction', 'Авто щойно куплено на аукціоні', 1),
(2, 'paid', 'Оплачено', 2),
(3, 'to_port', 'Їде в порт', 3),
(4, 'at_port', 'В порту', 4),
(5, 'in_sea', 'У морі', 5),
(6, 'in_klaipeda', 'У Клайпеді', 6),
(7, 'to_ukraine', 'Їде в Україну', 7),
(8, 'cleared_customs', 'Розмитнено', 8),
(9, 'in_ukraine', 'В Україні', 9);

-- ---------------------------------------------------------
-- Таблиця purchases
-- ---------------------------------------------------------
DROP TABLE IF EXISTS purchases;
CREATE TABLE purchases (
    purchase_id INT AUTO_INCREMENT PRIMARY KEY,
    vin_number VARCHAR(50) NOT NULL,
    car_make VARCHAR(50) NOT NULL,
    car_model VARCHAR(50) NOT NULL,
    car_year YEAR NOT NULL,
    buyer_id INT NOT NULL,
    country_id INT NOT NULL,
    auction_id INT NOT NULL,
    location_id INT NOT NULL,
    purchase_date DATE NOT NULL,
    price_usd DECIMAL(10,2) NOT NULL,
    status_id INT NOT NULL,
    estimated_arrival_date DATE,
    is_delivered BOOLEAN DEFAULT FALSE,
    notes TEXT,
    FOREIGN KEY (buyer_id) REFERENCES users(id),
    FOREIGN KEY (country_id) REFERENCES countries(country_id),
    FOREIGN KEY (auction_id) REFERENCES auctions(auction_id),
    FOREIGN KEY (location_id) REFERENCES locations(location_id),
    FOREIGN KEY (status_id) REFERENCES statuses(status_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO purchases (purchase_id, vin_number, car_make, car_model, car_year, buyer_id, country_id, auction_id, location_id, purchase_date, price_usd, status_id, estimated_arrival_date, is_delivered, notes)
VALUES
(1, '1HGBH41JXMN109186', 'Toyota', 'Camry', 2018, 1, 1, 1, 2, '2025-11-01', 8500.00, 3, '2025-11-30', FALSE,
 'Доставляється: Лос-Анджелес → Baltimore → Клайпеда → Україна'),
(2, 'JH4KA9650MC001234', 'Nissan', 'Note', 2016, 1, 3, 4, 4, '2025-10-20', 4200.00, 7, '2025-10-27', TRUE,
 'Європейська доставка: Берлін → Україна'),
(3, 'VF1AA000000123456', 'Mazda', 'CX-5', 2019, 2, 2, 3, 3, '2025-09-15', 11000.00, 6, '2025-10-10', FALSE,
 'Прибуло у Клайпеду, очікує відправку в Україну');

-- ---------------------------------------------------------
-- Таблиця purchase_images
-- ---------------------------------------------------------
DROP TABLE IF EXISTS purchase_images;
CREATE TABLE purchase_images (
    image_id INT AUTO_INCREMENT PRIMARY KEY,
    purchase_id INT NOT NULL,
    image_url VARCHAR(255) NOT NULL,
    image_type ENUM('auction','port','klaipeda') NOT NULL,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (purchase_id) REFERENCES purchases(purchase_id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO purchase_images (image_id, purchase_id, image_url, image_type, uploaded_at, notes)
VALUES
(1, 1, 'https://example.com/img/1_auction.jpg',  'auction',  '2025-11-01 12:00:00', 'Фото з аукціону'),
(2, 1, 'https://example.com/img/1_port.jpg',     'port',     '2025-11-05 08:30:00', 'Портове фото'),
(3, 3, 'https://example.com/img/3_klaipeda.jpg', 'klaipeda', '2025-10-10 09:00:00', 'Фото з Клайпеди');

