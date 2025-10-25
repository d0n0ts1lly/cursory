import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from mysql.connector import Error
from werkzeug.security import check_password_hash

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "23032023",
    "database": "copart_db",
    "port": 3306,
}


class LoginWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Авторизація")
        self.geometry("320x200")
        self.resizable(False, False)
        self.parent = parent

        frm = ttk.Frame(self, padding=12)
        frm.pack(fill="both", expand=True)

        ttk.Label(frm, text="Ім’я користувача:").pack(anchor="w", pady=(0,4))
        self.username_entry = ttk.Entry(frm)
        self.username_entry.pack(fill="x", pady=(0,8))

        ttk.Label(frm, text="Пароль:").pack(anchor="w", pady=(0,4))
        self.password_entry = ttk.Entry(frm, show="*")
        self.password_entry.pack(fill="x", pady=(0,10))

        btn = ttk.Button(frm, text="Увійти", command=self.login)
        btn.pack(fill="x")
        self.bind("<Return>", lambda e: self.login())

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showwarning("Помилка", "Введіть логін і пароль")
            return
        try:
            conn = mysql.connector.connect(**DB_CONFIG)
            cur = conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cur.fetchone()
            cur.close()
            conn.close()
            if not user:
                messagebox.showerror("Помилка", "Користувача не знайдено")
                return
            if not check_password_hash(user["password_hash"], password):
                messagebox.showerror("Помилка", "Невірний пароль")
                return
            self.parent.current_user = user
            messagebox.showinfo("Успішно", f"Вітаємо, {user['username']} ({user['role']})")
            self.destroy()
        except Error as e:
            messagebox.showerror("Помилка БД", str(e))


class MySQLViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Перегляд MySQL (з ролями)")
        self.geometry("1000x600")
        self.conn = None
        self.current_user = None
        self._setup_style()
        self._create_widgets()
        self.after(100, self.show_login)

    def _setup_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TFrame", padding=6)
        style.configure("TButton", padding=6, font=("Segoe UI", 10))
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=26)
        style.map("TButton", foreground=[("pressed", "black"), ("active", "black")])

    def show_login(self):
        login = LoginWindow(self)
        self.wait_window(login)
        if not self.current_user:
            self.quit()
            return
        self._update_ui_by_role()

    def _create_widgets(self):
        top = ttk.Frame(self)
        top.pack(fill="x", padx=10, pady=8)

        left_top = ttk.Frame(top)
        left_top.pack(side="left", fill="x", expand=True)

        ttk.Label(left_top, text="Назва таблиці:").pack(side="left", padx=(0,6))
        self.table_entry = ttk.Entry(left_top)
        self.table_entry.pack(side="left", padx=(0,8))
        self.table_entry.insert(0, "people")

        ttk.Button(left_top, text="Завантажити", command=self.load_table).pack(side="left", padx=(0,6))
        ttk.Button(left_top, text="Оновити", command=self.refresh).pack(side="left", padx=(0,6))

        right_top = ttk.Frame(top)
        right_top.pack(side="right")
        ttk.Button(right_top, text="Підключитись", command=self.connect_db).pack(side="left", padx=6)
        ttk.Button(right_top, text="Відключитись", command=self.disconnect_db).pack(side="left", padx=6)

        self.tree_frame = ttk.Frame(self)
        self.tree_frame.pack(fill="both", expand=True, padx=10, pady=(0,10))

        self.tree = ttk.Treeview(self.tree_frame, show="headings", selectmode="extended")
        vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        self.tree_frame.rowconfigure(0, weight=1)
        self.tree_frame.columnconfigure(0, weight=1)

        bottom = ttk.Frame(self)
        bottom.pack(fill="x", padx=10, pady=(0,10))

        self.add_btn = ttk.Button(bottom, text="Додати запис", command=self.add_record)
        self.del_btn = ttk.Button(bottom, text="Видалити вибране", command=self.delete_record)
        self.quit_btn = ttk.Button(bottom, text="Вийти", command=self.quit)

        # кнопки не додаємо в layout — відобразимо/приховаємо залежно від ролі після логіну
        self.quit_btn.pack(side="right")

        # підсвітка рядків
        self.tree.tag_configure('odd', background='#f7f7ff')
        self.tree.tag_configure('even', background='#ffffff')

    def _update_ui_by_role(self):
        role = (self.current_user.get("role", "") or "").lower()
        # спочатку прибираємо обидві кнопки (на випадок повторного виклику)
        try:
            self.add_btn.pack_forget()
            self.del_btn.pack_forget()
        except Exception:
            pass

        if role == "admin":
            self.add_btn.pack(side="left")
            self.del_btn.pack(side="left", padx=(6,0))
        # user не бачитиме цих кнопок
        # також можна заборонити контекстні меню та ін. сюди додати якщо потрібно

    def connect_db(self):
        if self.conn and self.conn.is_connected():
            messagebox.showinfo("Інфо", "Вже підключено")
            return
        try:
            self.conn = mysql.connector.connect(**DB_CONFIG)
            if self.conn.is_connected():
                messagebox.showinfo("Підключено", f"Підключено до {DB_CONFIG['database']}@{DB_CONFIG['host']}")
        except Error as e:
            messagebox.showerror("Помилка підключення", str(e))
            self.conn = None

    def disconnect_db(self):
        if self.conn:
            try:
                self.conn.close()
            except Exception:
                pass
        self.conn = None
        messagebox.showinfo("Відключено", "З'єднання закрито")

    def refresh(self):
        self.load_table()

    def _valid_table_name(self, table: str) -> bool:
        return bool(table) and table.replace("_", "").isalnum()

    def load_table(self):
        table = self.table_entry.get().strip()
        if not self._valid_table_name(table):
            messagebox.showwarning("Помилка", "Введіть коректну назву таблиці")
            return

        if not (self.conn and self.conn.is_connected()):
            try:
                self.conn = mysql.connector.connect(**DB_CONFIG)
            except Error as e:
                messagebox.showerror("Помилка підключення", str(e))
                return

        try:
            cur = self.conn.cursor()
            cur.execute(f"SELECT * FROM `{table}` LIMIT 1000")
            rows = cur.fetchall()
            cols = cur.column_names

            for c in self.tree["columns"]:
                self.tree.heading(c, text="")
            self.tree.delete(*self.tree.get_children())

            self.tree["columns"] = cols
            for col in cols:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=140, anchor="w")

            for i, row in enumerate(rows):
                tag = 'odd' if i % 2 else 'even'
                self.tree.insert("", "end", values=[str(v) if v is not None else "" for v in row], tags=(tag,))

            cur.close()
            messagebox.showinfo("Завантажено", f"{len(rows)} рядків (макс. 1000).")
        except Error as e:
            messagebox.showerror("Помилка запиту", str(e))

    def _get_table_columns(self, table: str):
        cur = self.conn.cursor()
        cur.execute(f"SHOW COLUMNS FROM `{table}`")
        cols_info = cur.fetchall()  # (Field, Type, Null, Key, Default, Extra)
        cur.close()
        return cols_info

    def _get_primary_key(self, table: str):
        cur = self.conn.cursor()
        cur.execute(f"SHOW KEYS FROM `{table}` WHERE Key_name = 'PRIMARY'")
        pk = cur.fetchone()
        cur.close()
        if pk:
            # структура: (Table, Non_unique, Key_name, Seq_in_index, Column_name, Collation, Cardinality, Sub_part, Packed, Null, Index_type, Comment, Index_comment)
            # Column_name at index 4
            return pk[4]
        return None

    def add_record(self):
        table = self.table_entry.get().strip()
        if not table or not self._valid_table_name(table):
            messagebox.showwarning("Помилка", "Вкажіть коректну таблицю")
            return
        if not (self.conn and self.conn.is_connected()):
            messagebox.showwarning("Помилка", "Немає з'єднання з БД")
            return

        try:
            cols_info = self._get_table_columns(table)
        except Error as e:
            messagebox.showerror("Помилка", str(e))
            return

        inputs = {}
        dlg = tk.Toplevel(self)
        dlg.title("Додавання запису")
        dlg.geometry("400x400")
        frm = ttk.Frame(dlg, padding=12)
        frm.pack(fill="both", expand=True)

        canvas = tk.Canvas(frm)
        scrollbar = ttk.Scrollbar(frm, orient="vertical", command=canvas.yview)
        scrollable = ttk.Frame(canvas)

        scrollable.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for field, coltype, null, key, default, extra in cols_info:
            if "auto_increment" in (extra or ""):
                continue
            lbl = ttk.Label(scrollable, text=f"{field} ({coltype})")
            lbl.pack(anchor="w", pady=(6,2))
            ent = ttk.Entry(scrollable)
            ent.pack(fill="x")
            if default is not None:
                ent.insert(0, str(default))
            inputs[field] = ent

        def on_submit():
            cols = []
            vals = []
            for f, ent in inputs.items():
                v = ent.get().strip()
                if v == "":
                    vals.append(None)
                else:
                    vals.append(v)
                cols.append(f)
            if not cols:
                messagebox.showwarning("Помилка", "Немає полів для вставки")
                return
            placeholders = ", ".join(["%s"] * len(cols))
            cols_sql = ", ".join([f"`{c}`" for c in cols])
            sql = f"INSERT INTO `{table}` ({cols_sql}) VALUES ({placeholders})"
            try:
                cur = self.conn.cursor()
                cur.execute(sql, tuple(vals))
                self.conn.commit()
                cur.close()
                messagebox.showinfo("Готово", "Запис додано")
                dlg.destroy()
                self.refresh()
            except Error as e:
                messagebox.showerror("Помилка вставки", str(e))

        btn_frame = ttk.Frame(dlg, padding=8)
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="Додати", command=on_submit).pack(side="right", padx=6)
        ttk.Button(btn_frame, text="Скасувати", command=dlg.destroy).pack(side="right")

    def delete_record(self):
        table = self.table_entry.get().strip()
        if not table or not self._valid_table_name(table):
            messagebox.showwarning("Помилка", "Вкажіть коректну таблицю")
            return
        if not (self.conn and self.conn.is_connected()):
            messagebox.showwarning("Помилка", "Немає з'єднання з БД")
            return

        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Вибір", "Оберіть рядки для видалення")
            return

        pk = self._get_primary_key(table)
        if not pk:
            messagebox.showerror("Помилка", "Не вдалось знайти первинний ключ таблиці. Видалення не виконано.")
            return

        if not messagebox.askyesno("Підтвердження", "Видалити обрані записи?"):
            return

        try:
            cur = self.conn.cursor()
            for item in selected:
                vals = self.tree.item(item)["values"]
                if not vals:
                    continue
                # знаходимо індекс стовпця із ім'ям pk
                try:
                    pk_index = list(self.tree["columns"]).index(pk)
                except ValueError:
                    messagebox.showerror("Помилка", "Первинний ключ не знайдено у стовпцях таблиці")
                    cur.close()
                    return
                pk_value = vals[pk_index]
                cur.execute(f"DELETE FROM `{table}` WHERE `{pk}` = %s", (pk_value,))
            self.conn.commit()
            cur.close()
            messagebox.showinfo("Готово", "Обрані записи видалено")
            self.refresh()
        except Error as e:
            messagebox.showerror("Помилка видалення", str(e))


if __name__ == "__main__":
    app = MySQLViewer()
    app.mainloop()
