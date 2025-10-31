import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk, messagebox
from mysql.connector import Error
from views.components.dialogs import ModernCRUDDialog
from config.database import DatabaseManager

class AdminCRUDView:
    """CRUD операции для админской панели"""
    
    def __init__(self, parent, connection):
        self.parent = parent
        self.conn = connection
        self.db_manager = DatabaseManager(connection)
    
    def open_table(self, table):
        """Открытие таблицы для админа с возможностью CRUD"""
        if not (self.conn and self.conn.is_connected()):
            messagebox.showwarning("Помилка", "Немає з'єднання з БД")
            return

        # Получаем колонки и данные
        try:
            cur = self.conn.cursor()
            cur.execute(f"SELECT * FROM `{table}` LIMIT 100")
            rows = cur.fetchall()
            cols = [description[0] for description in cur.description]
            cur.close()
        except Error as e:
            messagebox.showerror("Помилка БД", f"Помилка завантаження таблиці {table}: {str(e)}")
            return

        # Создаем окно
        win = tb.Toplevel(self.parent)
        win.title(f"Адмін: {table}")
        win.geometry("1200x700")

        # Основной контейнер
        main_frame = tb.Frame(win)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Заголовок
        tb.Label(main_frame, text=f"Таблиця: {table}", 
                font=("Segoe UI", 16, "bold")).pack(pady=(0, 10))

        # Фрейм с Treeview и скроллбарами
        tree_frame = tb.Frame(main_frame)
        tree_frame.pack(fill="both", expand=True, pady=5)

        # Создаем Treeview
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=20)
        
        # Скроллбары
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Размещаем элементы
        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Настройка колонок
        for col in cols:
            tree.heading(col, text=col)
            tree.column(col, width=120, minwidth=80, anchor="w")

        # Вставка данных
        for i, row in enumerate(rows):
            tree.insert("", "end", values=row, tags=('even',) if i % 2 == 0 else ('odd',))

        # Настройка цветов строк
        tree.tag_configure('odd', background='#f8f9fa')
        tree.tag_configure('even', background='#ffffff')

        # Фрейм с кнопками
        btn_frame = tb.Frame(main_frame)
        btn_frame.pack(fill="x", pady=10)

        def refresh_table():
            """Обновление таблицы"""
            try:
                tree.delete(*tree.get_children())
                cur = self.conn.cursor()
                cur.execute(f"SELECT * FROM `{table}` LIMIT 100")
                rows = cur.fetchall()
                for i, row in enumerate(rows):
                    tree.insert("", "end", values=row, tags=('even',) if i % 2 == 0 else ('odd',))
                cur.close()
                messagebox.showinfo("Оновлено", "Таблицю оновлено")
            except Error as e:
                messagebox.showerror("Помилка", f"Помилка оновлення: {str(e)}")

        def add_record():
            def save_data(data, mode):
                try:
                    cur = self.conn.cursor()
                    columns = ', '.join([f"`{k}`" for k in data.keys()])
                    placeholders = ', '.join(['%s'] * len(data))
                    sql = f"INSERT INTO `{table}` ({columns}) VALUES ({placeholders})"
                    cur.execute(sql, tuple(data.values()))
                    self.conn.commit()
                    cur.close()
                    messagebox.showinfo("Успіх", "Запис успішно додано!")
                    refresh_table()
                except Error as e:
                    messagebox.showerror("Помилка", f"Помилка додавання: {str(e)}")

            ModernCRUDDialog(self.parent, f"Додати запис у {table}", table, "add", on_save=save_data)

        def edit_record():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Помилка", "Оберіть рядок для редагування")
                return
            
            pk = self.db_manager.get_primary_key(table)
            if not pk:
                messagebox.showerror("Помилка", "Не знайдено первинний ключ")
                return
            
            item = tree.item(selected[0])
            values = item["values"]
            pk_index = cols.index(pk)
            pk_value = values[pk_index]

            # Собираем данные для редактирования
            data = {}
            for i, col in enumerate(cols):
                data[col] = values[i] if i < len(values) else ""

            def save_data(updated_data, mode):
                try:
                    cur = self.conn.cursor()
                    set_clause = ', '.join([f"`{k}`=%s" for k in updated_data.keys()])
                    sql = f"UPDATE `{table}` SET {set_clause} WHERE `{pk}`=%s"
                    values_list = list(updated_data.values())
                    values_list.append(pk_value)
                    cur.execute(sql, tuple(values_list))
                    self.conn.commit()
                    cur.close()
                    messagebox.showinfo("Успіх", "Запис успішно оновлено!")
                    refresh_table()
                except Error as e:
                    messagebox.showerror("Помилка", f"Помилка оновлення: {str(e)}")

            ModernCRUDDialog(self.parent, f"Редагувати запис у {table}", table, "edit", data, on_save=save_data)

        def delete_record():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Помилка", "Оберіть рядки для видалення")
                return
            
            pk = self.db_manager.get_primary_key(table)
            if not pk:
                messagebox.showerror("Помилка", "Не знайдено первинний ключ")
                return
            
            if not messagebox.askyesno("Підтвердження", 
                                     f"Видалити {len(selected)} обраних записів?"):
                return
            
            try:
                cur = self.conn.cursor()
                for item in selected:
                    vals = tree.item(item)["values"]
                    pk_index = tree["columns"].index(pk)
                    pk_value = vals[pk_index]
                    cur.execute(f"DELETE FROM `{table}` WHERE `{pk}`=%s", (pk_value,))
                
                self.conn.commit()
                cur.close()
                
                messagebox.showinfo("Успіх", "Записи успішно видалено!")
                refresh_table()
                
            except Error as e:
                messagebox.showerror("Помилка", f"Помилка видалення: {str(e)}")

        def show_table_stats():
            """Показ статистики по таблице"""
            try:
                cur = self.conn.cursor()
                cur.execute(f"SELECT COUNT(*) as total FROM `{table}`")
                total = cur.fetchone()[0]
                cur.close()
                
                messagebox.showinfo("Статистика", 
                                  f"Таблиця: {table}\n"
                                  f"Всього записів: {total}")
            except Error as e:
                messagebox.showerror("Помилка", f"Помилка отримання статистики: {str(e)}")

        # Кнопки управления
        tb.Button(btn_frame, text="🔄 Оновити", bootstyle="info",
                 command=refresh_table).pack(side="left", padx=5)
        tb.Button(btn_frame, text="➕ Додати", bootstyle="success",
                 command=add_record).pack(side="left", padx=5)
        tb.Button(btn_frame, text="✏️ Редагувати", bootstyle="warning",
                 command=edit_record).pack(side="left", padx=5)
        tb.Button(btn_frame, text="🗑️ Видалити", bootstyle="danger",
                 command=delete_record).pack(side="left", padx=5)
        tb.Button(btn_frame, text="📊 Статистика", bootstyle="secondary",
                 command=show_table_stats).pack(side="left", padx=5)
        tb.Button(btn_frame, text="Закрити", bootstyle="dark",
                 command=win.destroy).pack(side="right", padx=5)