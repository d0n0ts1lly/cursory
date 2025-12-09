import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash
from config import DB_CONFIG

class DatabaseInitializer:
    @staticmethod
    def initialize_database():
        try:
            config = DB_CONFIG.copy()
            config.pop('database', None)
            conn = mysql.connector.connect(**config)
            cursor = conn.cursor()
            
            cursor.execute("CREATE DATABASE IF NOT EXISTS shipping_db")
            cursor.execute("USE shipping_db")
            
            DatabaseInitializer._create_tables(cursor)
            
            DatabaseInitializer._initialize_data_if_empty(cursor)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print("✅ База даних успішно ініціалізована")
            return True
            
        except Error as e:
            print(f"❌ Помилка ініціалізації бази даних: {e}")
            return False
    
    @staticmethod
    def _create_tables(cursor):
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(100) NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                role ENUM('admin','user') NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                phone VARCHAR(20),
                email VARCHAR(100)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS countries (
                country_id INT AUTO_INCREMENT PRIMARY KEY,
                country_name VARCHAR(100) NOT NULL UNIQUE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ports (
                port_id INT AUTO_INCREMENT PRIMARY KEY,
                port_name VARCHAR(100) NOT NULL,
                country_id INT NOT NULL,
                delivery_to_europe_days INT NOT NULL,
                FOREIGN KEY (country_id) REFERENCES countries(country_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS auctions (
                auction_id INT AUTO_INCREMENT PRIMARY KEY,
                auction_name VARCHAR(100) NOT NULL,
                country_id INT NOT NULL,
                FOREIGN KEY (country_id) REFERENCES countries(country_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS locations (
                location_id INT AUTO_INCREMENT PRIMARY KEY,
                location_name VARCHAR(100) NOT NULL,
                country_id INT NOT NULL,
                default_port_id INT NOT NULL,
                days_to_port INT NOT NULL,
                FOREIGN KEY (country_id) REFERENCES countries(country_id),
                FOREIGN KEY (default_port_id) REFERENCES ports(port_id)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS statuses (
                status_id INT AUTO_INCREMENT PRIMARY KEY,
                status_key VARCHAR(50) NOT NULL UNIQUE,
                status_name VARCHAR(100) NOT NULL,
                order_index INT NOT NULL
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS purchases (
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
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS purchase_images (
                image_id INT AUTO_INCREMENT PRIMARY KEY,
                purchase_id INT NOT NULL,
                image_url VARCHAR(255) NOT NULL,
                image_type ENUM('auction','port','klaipeda') NOT NULL,
                uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (purchase_id) REFERENCES purchases(purchase_id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
        """)
    
    @staticmethod
    def _initialize_data_if_empty(cursor):
        cursor.execute("SELECT COUNT(*) FROM statuses")
        if cursor.fetchone()[0] == 0:
            statuses = [
                ('bought_auction', 'Авто щойно куплено на аукціоні', 1),
                ('paid', 'Оплачено', 2),
                ('to_port', 'Їде в порт', 3),
                ('at_port', 'В порту', 4),
                ('in_sea', 'У морі', 5),
                ('in_klaipeda', 'У Клайпеді', 6),
                ('to_ukraine', 'Їде в Україну', 7),
                ('cleared_customs', 'Розмитнено', 8),
                ('in_ukraine', 'В Україні', 9)
            ]
            cursor.executemany("INSERT INTO statuses (status_key, status_name, order_index) VALUES (%s, %s, %s)", statuses)
        
        cursor.execute("SELECT COUNT(*) FROM countries")
        if cursor.fetchone()[0] == 0:
            countries = [
                ('Сполучені Штати Америки',),
                ('Японія',),
                ('Німеччина',),
                ('Китай',),
                ('Литва',),
                ('Польща',)
            ]
            cursor.executemany("INSERT INTO countries (country_name) VALUES (%s)", countries)
        
        cursor.execute("SELECT country_id, country_name FROM countries")
        country_map = {name: id for id, name in cursor.fetchall()}
        
        cursor.execute("SELECT COUNT(*) FROM ports")
        if cursor.fetchone()[0] == 0:
            ports = [
                ('Baltimore', country_map['Сполучені Штати Америки'], 14),
                ('Yokohama', country_map['Японія'], 16),
                ('Hamburg', country_map['Німеччина'], 2),
                ('Shanghai', country_map['Китай'], 20),
                ('Klaipėda', country_map['Литва'], 0),
                ('Gdynia', country_map['Польща'], 1)
            ]
            cursor.executemany("INSERT INTO ports (port_name, country_id, delivery_to_europe_days) VALUES (%s, %s, %s)", ports)
        
        cursor.execute("SELECT port_id, port_name FROM ports")
        port_map = {name: id for id, name in cursor.fetchall()}
        
        cursor.execute("SELECT COUNT(*) FROM auctions")
        if cursor.fetchone()[0] == 0:
            auctions = [
                ('Copart USA', country_map['Сполучені Штати Америки']),
                ('IAAI USA', country_map['Сполучені Штати Америки']),
                ('USS Japan', country_map['Японія']),
                ('Autorola Germany', country_map['Німеччина']),
                ('Copart China', country_map['Китай']),
                ('Baltic Auctions LT', country_map['Литва'])
            ]
            cursor.executemany("INSERT INTO auctions (auction_name, country_id) VALUES (%s, %s)", auctions)
        
        cursor.execute("SELECT COUNT(*) FROM locations")
        if cursor.fetchone()[0] == 0:
            locations = [
                ('Маямі (США)', country_map['Сполучені Штати Америки'], port_map['Baltimore'], 3),
                ('Лос-Анджелес (США)', country_map['Сполучені Штати Америки'], port_map['Baltimore'], 5),
                ('Токіо (Японія)', country_map['Японія'], port_map['Yokohama'], 1),
                ('Берлін (Німеччина)', country_map['Німеччина'], port_map['Hamburg'], 1),
                ('Шанхай (Китай)', country_map['Китай'], port_map['Shanghai'], 2),
                ('Вільнюс (Литва)', country_map['Литва'], port_map['Klaipėda'], 1),
                ('Варшава (Польща)', country_map['Польща'], port_map['Gdynia'], 1)
            ]
            cursor.executemany("INSERT INTO locations (location_name, country_id, default_port_id, days_to_port) VALUES (%s, %s, %s, %s)", locations)
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'demo_user'")
        if cursor.fetchone()[0] == 0:
            demo_password = generate_password_hash("demo123")
            cursor.execute("""
                INSERT INTO users (username, password_hash, role, phone, email) 
                VALUES (%s, %s, %s, %s, %s)
            """, ("demo_user", demo_password, "admin", "+380123456789", "demo@autotracker.com"))
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE username = 'user1'")
        if cursor.fetchone()[0] == 0:
            user_password = generate_password_hash("user123")
            cursor.execute("""
                INSERT INTO users (username, password_hash, role, phone, email) 
                VALUES (%s, %s, %s, %s, %s)
            """, ("user1", user_password, "user", "+380987654321", "user1@autotracker.com"))