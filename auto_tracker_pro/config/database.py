import mysql.connector
from mysql.connector import Error
from tkinter import messagebox
from config.settings import Config

def safe_connect():
    """
    Безопасное подключение к базе данных
    Возвращает connection или None в случае ошибки
    """
    try:
        conn = mysql.connector.connect(**Config.DB_CONFIG)
        return conn
    except Exception as e:
        messagebox.showerror("DB Error", f"Не вдалося підключитись: {e}")
        return None

def fetchone_dict(cur):
    """
    Преобразует результат запроса в словарь
    """
    if cur.description is None:
        return None
        
    cols = [c[0] for c in cur.description]
    row = cur.fetchone()
    if row is None:
        return None
    return dict(zip(cols, row))

def fetchall_dict(cur):
    """
    Преобразует все результаты запроса в список словарей
    """
    if cur.description is None:
        return []
        
    cols = [c[0] for c in cur.description]
    rows = cur.fetchall()
    return [dict(zip(cols, row)) for row in rows]

class DatabaseManager:
    """Менеджер для работы с базой данных"""
    
    def __init__(self, connection):
        self.conn = connection
    
    def get_table_columns(self, table):
        """Получение информации о колонках таблицы"""
        if not self.conn:
            return []
        
        try:
            cur = self.conn.cursor()
            cur.execute(f"SHOW COLUMNS FROM `{table}`")
            columns = cur.fetchall()
            cur.close()
            return columns
        except Error as e:
            print(f"Error getting columns: {e}")
            return []
    
    def get_primary_key(self, table):
        """Получение первичного ключа таблицы"""
        columns = self.get_table_columns(table)
        for col in columns:
            if col[3] == 'PRI':  # PRI indicates primary key
                return col[0]
        return None
    
    def is_foreign_key(self, table, column):
        """Проверяет, является ли поле внешним ключом"""
        try:
            cur = self.conn.cursor()
            cur.execute(f"""
                SELECT CONSTRAINT_NAME 
                FROM information_schema.KEY_COLUMN_USAGE 
                WHERE TABLE_NAME = '{table}' 
                AND COLUMN_NAME = '{column}' 
                AND REFERENCED_TABLE_NAME IS NOT NULL
            """)
            result = cur.fetchone()
            cur.close()
            return result is not None
        except Error:
            return False
    
    def get_foreign_key_info(self, table, column):
        """Получает информацию о внешнем ключе"""
        try:
            cur = self.conn.cursor()
            cur.execute(f"""
                SELECT REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME 
                FROM information_schema.KEY_COLUMN_USAGE 
                WHERE TABLE_NAME = '{table}' 
                AND COLUMN_NAME = '{column}' 
                AND REFERENCED_TABLE_NAME IS NOT NULL
            """)
            result = cur.fetchone()
            cur.close()
            return result if result else (None, None)
        except Error:
            return (None, None)
    
    def get_foreign_key_values(self, table, column):
        """Получает значения для внешнего ключа"""
        try:
            cur = self.conn.cursor()
            # Пытаемся найти текстовое представление
            cur.execute(f"SHOW COLUMNS FROM `{table}`")
            cols = cur.fetchall()
            
            # Ищем поле с названием
            display_column = None
            for col in cols:
                if col[0] in ['name', 'username', 'country_name', 'status_name', 'car_make']:
                    display_column = col[0]
                    break
            
            if display_column:
                cur.execute(f"SELECT {column}, {display_column} FROM `{table}`")
            else:
                cur.execute(f"SELECT {column} FROM `{table}`")
                display_column = column
            
            rows = cur.fetchall()
            cur.close()
            
            if len(rows[0]) > 1:
                return [f"{row[0]} - {row[1]}" for row in rows]
            else:
                return [str(row[0]) for row in rows]
                
        except Error as e:
            print(f"Error getting foreign key values: {e}")
            return []