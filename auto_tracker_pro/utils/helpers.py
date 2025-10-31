import csv
from tkinter import filedialog, messagebox
from mysql.connector import Error

def export_to_csv(conn, query, filename, params=None):
    """
    Экспорт данных в CSV файл
    """
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        initialfile=filename
    )
    
    if not file_path:
        return False
    
    try:
        cur = conn.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
            
        rows = cur.fetchall()
        cols = [i[0] for i in cur.description]
        cur.close()

        with open(file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(cols)
            writer.writerows(rows)

        messagebox.showinfo("Успіх", f"Дані експортовано в {file_path}")
        return True
        
    except Error as e:
        messagebox.showerror("Помилка", f"Помилка експорту: {e}")
        return False

def validate_required_fields(fields, data):
    """
    Валидация обязательных полей
    """
    for field in fields:
        if not data.get(field):
            return False, f"Поле '{field}' обов'язкове для заповнення"
    return True, ""

def format_date(date_obj):
    """
    Форматирование даты для отображения
    """
    if hasattr(date_obj, 'strftime'):
        return date_obj.strftime("%d.%m.%Y")
    return str(date_obj)

def get_status_color(status_name):
    """
    Возвращает цвет статуса в зависимости от его названия
    """
    status_name_lower = status_name.lower()
    if "доставлено" in status_name_lower:
        return "success"
    elif "в дорозі" in status_name_lower or "обробка" in status_name_lower:
        return "warning"
    elif "скасовано" in status_name_lower:
        return "danger"
    else:
        return "secondary"