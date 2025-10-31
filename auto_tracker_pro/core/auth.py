from werkzeug.security import check_password_hash, generate_password_hash
from mysql.connector import Error
from tkinter import messagebox
from config.database import safe_connect

class AuthManager:
    """Менеджер аутентификации"""
    
    def __init__(self):
        self.current_user = None
        self.connection = None
    
    def login(self, username, password):
        """
        Аутентификация пользователя
        Возвращает user_data при успехе, None при неудаче
        """
        if not username or not password:
            messagebox.showwarning("Помилка", "Введіть логін та пароль")
            return None
        
        conn = safe_connect()
        if not conn:
            return None
            
        cur = conn.cursor(dictionary=True)
        try:
            cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cur.fetchone()
            
            if not user:
                messagebox.showerror("Помилка", "Користувача не знайдено")
                cur.close()
                conn.close()
                return None
                
            if not check_password_hash(user["password_hash"], password):
                messagebox.showerror("Помилка", "Невірний пароль")
                cur.close()
                conn.close()
                return None
                
            self.current_user = user
            self.connection = conn
            cur.close()
            return user
            
        except Error as e:
            messagebox.showerror("DB Error", str(e))
            cur.close()
            conn.close()
            return None
    
    def logout(self):
        """Выход из системы"""
        if self.connection:
            try:
                self.connection.close()
            except:
                pass
        self.current_user = None
        self.connection = None
    
    def is_authenticated(self):
        """Проверка аутентификации"""
        return self.current_user is not None
    
    def is_admin(self):
        """Проверка роли администратора"""
        return self.current_user and self.current_user.get("role") == "admin"
    
    def get_user_id(self):
        """Получение ID текущего пользователя"""
        return self.current_user.get("id") if self.current_user else None
    
    def get_username(self):
        """Получение имени текущего пользователя"""
        return self.current_user.get("username") if self.current_user else None
    
    def demo_login(self):
        """Демо-вход для тестирования"""
        return {
            "username": "demo_user",
            "password": "demo123"
        }