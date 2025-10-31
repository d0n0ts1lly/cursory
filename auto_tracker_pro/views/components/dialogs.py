import datetime
from tkinter import ttk as tkttk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from config.database import DatabaseManager

class ModernCRUDDialog:
    """Современный диалог для CRUD операций"""
    
    def __init__(self, parent, title, table, mode="add", data=None, on_save=None):
        self.parent = parent
        self.title = title
        self.table = table
        self.mode = mode
        self.data = data or {}
        self.on_save = on_save
        self.entries = {}
        self.foreign_keys = {}
        
        self.db_manager = DatabaseManager(parent.conn)
        self._create_dialog()
        
    def _create_dialog(self):
        self.dlg = tb.Toplevel(self.parent)
        self.dlg.title(self.title)
        self.dlg.geometry("600x700")
        self.dlg.transient(self.parent)
        self.dlg.grab_set()
        
        # Header
        header = tb.Frame(self.dlg, bootstyle="primary", padding=20)
        header.pack(fill="x")
        
        tb.Label(header, text=self.title, font=("Segoe UI", 18, "bold"),
                bootstyle="inverse-primary").pack()
        
        # Main content with scroll
        main_container = tb.Frame(self.dlg)
        main_container.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Create scrollable frame
        canvas = tb.Canvas(main_container, height=500)
        scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tb.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Load form fields
        self._load_form_fields()
        
        # Buttons
        self._create_buttons()
        
    def _load_form_fields(self):
        """Загружает поля формы на основе структуры таблицы"""
        if not self.parent.conn:
            return
            
        cols_info = self.db_manager.get_table_columns(self.table)
        self.entries = {}
        
        for idx, (field, coltype, null, key, default, extra) in enumerate(cols_info):
            # Пропускаем auto_increment поля при добавлении
            if self.mode == "add" and "auto_increment" in (extra or ""):
                continue
                
            # Создаем контейнер для поля
            field_frame = tb.Frame(self.scrollable_frame)
            field_frame.pack(fill="x", pady=8)
            
            # Метка поля
            label_text = f"{field} ({coltype})"
            if null == "NO":
                label_text += " *"
                
            tb.Label(field_frame, text=label_text, font=("Segoe UI", 10, "bold"),
                    bootstyle="primary").pack(anchor="w", pady=(0, 5))
            
            # Создаем поле ввода в зависимости от типа
            entry = self._create_input_field(field, coltype, default, idx)
            entry.pack(fill="x", pady=2)
            self.entries[field] = entry
            
    def _create_input_field(self, field, coltype, default, idx):
        """Создает поле ввода соответствующего типа"""
        value = self.data.get(field, "")
        
        # Проверяем, является ли поле внешним ключом
        is_foreign_key = self.db_manager.is_foreign_key(self.table, field)
        
        if is_foreign_key:
            # Для внешних ключей создаем выпадающий список
            ref_table, ref_column = self.db_manager.get_foreign_key_info(self.table, field)
            values = self.db_manager.get_foreign_key_values(ref_table, ref_column)
            
            var = tb.StringVar(value=str(value) if value else "")
            entry = tb.Combobox(self.scrollable_frame, textvariable=var, values=values,
                              font=("Segoe UI", 10))
            self.foreign_keys[field] = (ref_table, ref_column)
            
        elif "enum" in coltype.lower():
            # ENUM поле - Combobox
            enum_values = coltype.split("'")[1::2]
            var = tb.StringVar(value=value if value else enum_values[0] if enum_values else "")
            entry = tb.Combobox(self.scrollable_frame, textvariable=var, values=enum_values,
                              font=("Segoe UI", 10))
            
        elif "date" in coltype.lower():
            # DATE поле с календарем
            frame = tb.Frame(self.scrollable_frame)
            var = tb.StringVar(value=value if value else datetime.date.today().isoformat())
            entry = tb.Entry(frame, textvariable=var, font=("Segoe UI", 10))
            entry.pack(side="left", fill="x", expand=True)
            
            # Кнопка календаря
            tb.Button(frame, text="📅", bootstyle="outline-secondary",
                     command=lambda: self._show_calendar(var)).pack(side="right", padx=(5, 0))
            return frame
            
        elif "text" in coltype.lower() or ("varchar" in coltype.lower() and 
                                         int(coltype.split("(")[1].split(")")[0]) > 50):
            # TEXT или длинный VARCHAR - Text widget
            frame = tb.Frame(self.scrollable_frame)
            entry = tb.Text(frame, height=4, font=("Segoe UI", 10))
            if value:
                entry.insert("1.0", str(value))
            entry.pack(fill="both", expand=True)
            return frame
            
        elif "int" in coltype.lower() or "decimal" in coltype.lower():
            # Числовое поле
            var = tb.StringVar(value=str(value) if value else "")
            entry = tb.Entry(self.scrollable_frame, textvariable=var, font=("Segoe UI", 10))
            
        else:
            # Стандартное текстовое поле
            var = tb.StringVar(value=str(value) if value else "")
            entry = tb.Entry(self.scrollable_frame, textvariable=var, font=("Segoe UI", 10))
            
        return entry
        
    def _show_calendar(self, var):
        """Показывает календарь для выбора даты"""
        cal_win = tb.Toplevel(self.dlg)
        cal_win.title("Виберіть дату")
        cal_win.geometry("300x300")
        
        # Простой календарь
        cal = tkttk.Calendar(cal_win, selectmode='day')
        cal.pack(padx=10, pady=10)
        
        def set_date():
            var.set(cal.get_date())
            cal_win.destroy()
            
        tb.Button(cal_win, text="Обрати", bootstyle="success",
                 command=set_date).pack(pady=10)
        
    def _create_buttons(self):
        """Создает кнопки действий"""
        btn_frame = tb.Frame(self.dlg)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        tb.Button(btn_frame, text="💾 Зберегти", bootstyle="success",
                 command=self._save, width=15).pack(side="left", padx=5)
        tb.Button(btn_frame, text="❌ Скасувати", bootstyle="secondary",
                 command=self.dlg.destroy, width=15).pack(side="right", padx=5)
        
    def _save(self):
        """Сохраняет данные"""
        try:
            data = {}
            cols_info = self.db_manager.get_table_columns(self.table)
            
            for field, coltype, null, key, default, extra in cols_info:
                if field not in self.entries:
                    continue
                    
                widget = self.entries[field]
                value = self._get_widget_value(widget, field)
                
                # Валидация обязательных полей
                if null == "NO" and not value:
                    tb.messagebox.showerror("Помилка", f"Поле '{field}' обов'язкове для заповнення")
                    return
                    
                # Преобразование типов
                value = self._convert_value_type(value, coltype, field)
                if value is None:
                    return
                
                data[field] = value
            
            # Вызываем callback для сохранения
            if self.on_save:
                self.on_save(data, self.mode)
                
            self.dlg.destroy()
            
        except Exception as e:
            tb.messagebox.showerror("Помилка", f"Помилка збереження: {str(e)}")
    
    def _get_widget_value(self, widget, field):
        """Получает значение из виджета"""
        if isinstance(widget, tb.Combobox):
            value = widget.get()
            # Для внешних ключей берем только ID
            if field in self.foreign_keys:
                if value and ' - ' in value:
                    value = value.split(' - ')[0]
        elif hasattr(widget, 'winfo_class') and widget.winfo_class() == 'Text':
            value = widget.get("1.0", "end-1c")
        elif hasattr(widget, 'winfo_class') and widget.winfo_class() == 'Frame':
            # Для полей с дополнительными элементами
            for child in widget.winfo_children():
                if child.winfo_class() == 'Entry':
                    value = child.get()
                    break
            else:
                value = ""
        else:
            value = widget.get()
        return value
    
    def _convert_value_type(self, value, coltype, field):
        """Преобразует значение к нужному типу"""
        if not value:
            return None
            
        if "int" in coltype.lower() and value:
            try:
                return int(value)
            except ValueError:
                tb.messagebox.showerror("Помилка", f"Поле '{field}' має бути числом")
                return None
        elif "decimal" in coltype.lower() and value:
            try:
                return float(value)
            except ValueError:
                tb.messagebox.showerror("Помилка", f"Поле '{field}' має бути числом")
                return None
        elif "year" in coltype.lower() and value:
            try:
                return int(value)
            except ValueError:
                tb.messagebox.showerror("Помилка", f"Поле '{field}' має бути роком")
                return None
        return value