import mysql.connector
from mysql.connector import Error
from tkinter import messagebox
from config import DB_CONFIG

def safe_connect():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        messagebox.showerror("Помилка БД", f"Не вдалося підключитися: {e}")
        return None