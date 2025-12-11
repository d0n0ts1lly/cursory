import datetime
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import ttk, messagebox
from werkzeug.security import generate_password_hash
from .calendar_dialog import CalendarDialog
from tkinter import Canvas


class ModernCRUDDialog:
    def __init__(self, parent, title, table, mode="add", data=None, on_save=None):
        self.parent = parent
        self.title = title
        self.table = table
        self.mode = mode
        self.data = data or {}
        self.on_save = on_save
        self.field_widgets = {}
        self.foreign_keys = {}

        self.is_purchases = (self.table == "purchases")
        self._status_key_map = None

        self._create_dialog()


    def _create_dialog(self):
        self.dlg = tb.Toplevel(self.parent)
        self.dlg.title(self.title)
        self.dlg.geometry("650x700")
        self.dlg.transient(self.parent)
        self.dlg.grab_set()

        self.dlg.update_idletasks()
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()

        x = parent_x + (parent_width - 650) // 2
        y = parent_y + (parent_height - 700) // 2
        self.dlg.geometry(f"+{x}+{y}")

        header = tb.Frame(self.dlg, bootstyle="primary", padding=15)
        header.pack(fill="x")

        tb.Label(
            header,
            text=self.title,
            font=("Segoe UI", 16, "bold"),
            bootstyle="inverse-primary"
        ).pack()

        main_container = tb.Frame(self.dlg)
        main_container.pack(fill="both", expand=True, padx=20, pady=10)

        canvas = Canvas(main_container, height=500)
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

        self._load_form_fields()
        self._create_buttons()


    def _load_form_fields(self):
        if not hasattr(self.parent, 'conn'):
            return

        cols_info = self.parent._get_table_columns(self.table)
        self.field_widgets = {}

        for field, coltype, null, key, default, extra in cols_info:
            if self.mode == "add" and extra and "auto_increment" in extra.lower():
                continue

            if field in ['created_at', 'uploaded_at']:
                continue

            field_frame = tb.Frame(self.scrollable_frame)
            field_frame.pack(fill="x", pady=8)

            label_text = f"{field}"
            if null == "NO" and not (field == "password_hash" and self.mode == "edit"):
                label_text += " *"

            tb.Label(
                field_frame,
                text=label_text,
                font=("Segoe UI", 10, "bold"),
                bootstyle="primary"
            ).pack(anchor="w", pady=(0, 3))

            widget_info = self._create_input_field(field, coltype, self.data.get(field, ""))
            widget_info['widget'].pack(fill="x", pady=2)

            self.field_widgets[field] = {
                'widget': widget_info['widget'],
                'type': widget_info['type'],
                'coltype': coltype,
                'required': null == "NO" and not (field == "password_hash" and self.mode == "edit"),
                'var': widget_info.get('var')
            }

            self._attach_purchases_logic(field, self.field_widgets[field])

        if self.is_purchases:
            self._init_purchases_relations()

    def _create_input_field(self, field, coltype, value):
        if field == "password_hash":
            frame = tb.Frame(self.scrollable_frame)
            var = tb.StringVar(value=value if value else "")
            entry = tb.Entry(frame, textvariable=var, show="•", font=("Segoe UI", 10))
            entry.pack(side="left", fill="x", expand=True)

            def toggle_password():
                if entry.cget('show') == '':
                    entry.config(show='•')
                    toggle_btn.config(text='👁️')
                else:
                    entry.config(show='')
                    toggle_btn.config(text='🔒')

            toggle_btn = tb.Button(
                frame,
                text="👁️",
                bootstyle="outline-secondary",
                command=toggle_password,
                width=3
            )
            toggle_btn.pack(side="right", padx=(5, 0))

            return {'widget': frame, 'type': 'password', 'var': var}

        is_foreign_key = self.parent._is_foreign_key(self.table, field)
        if is_foreign_key:
            ref_table, ref_column = self.parent._get_foreign_key_info(self.table, field)
            values = self.parent._get_foreign_key_values(ref_table, ref_column)

            display_value = ""
            if value:
                for val in values:
                    if str(value) in val:
                        display_value = val
                        break
                if not display_value:
                    display_value = str(value)

            var = tb.StringVar(value=display_value)
            combobox = tb.Combobox(
                self.scrollable_frame,
                textvariable=var,
                values=values,
                font=("Segoe UI", 10),
                state="readonly"
            )
            self.foreign_keys[field] = (ref_table, ref_column)

            return {'widget': combobox, 'type': 'foreign_key', 'var': var}

        if "enum" in coltype.lower():
            enum_values = coltype.split("'")[1::2]
            var = tb.StringVar(value=value if value else enum_values[0] if enum_values else "")
            combobox = tb.Combobox(
                self.scrollable_frame,
                textvariable=var,
                values=enum_values,
                font=("Segoe UI", 10),
                state="readonly"
            )
            return {'widget': combobox, 'type': 'enum', 'var': var}

        elif "date" in coltype.lower() or "timestamp" in coltype.lower():
            frame = tb.Frame(self.scrollable_frame)
            current_value = value if value else datetime.datetime.now().strftime("%Y-%m-%d")
            var = tb.StringVar(value=current_value)
            entry = tb.Entry(frame, textvariable=var, font=("Segoe UI", 10))
            entry.pack(side="left", fill="x", expand=True)

            def show_calendar():
                calendar = CalendarDialog(self.dlg)
                date_str = calendar.show()
                if date_str:
                    var.set(date_str)

            tb.Button(
                frame,
                text="📅",
                bootstyle="outline-secondary",
                command=show_calendar,
                width=3
            ).pack(side="right", padx=(5, 0))

            return {'widget': frame, 'type': 'date', 'var': var}

        elif "text" in coltype.lower():
            text_widget = tb.Text(self.scrollable_frame, height=4, font=("Segoe UI", 10))
            if value:
                text_widget.insert("1.0", str(value))
            return {'widget': text_widget, 'type': 'text'}

        elif "int" in coltype.lower() or "decimal" in coltype.lower() or "float" in coltype.lower():
            var = tb.StringVar(value=str(value) if value else "0")
            entry = tb.Entry(self.scrollable_frame, textvariable=var, font=("Segoe UI", 10))
            return {'widget': entry, 'type': 'numeric', 'var': var}

        elif "year" in coltype.lower():
            current_year = datetime.datetime.now().year
            years = [str(y) for y in range(current_year - 30, current_year + 1)]
            var = tb.StringVar(value=str(value) if value else str(current_year))
            combobox = tb.Combobox(
                self.scrollable_frame,
                textvariable=var,
                values=years,
                font=("Segoe UI", 10)
            )
            return {'widget': combobox, 'type': 'year', 'var': var}

        else:
            var = tb.StringVar(value=str(value) if value else "")
            entry = tb.Entry(self.scrollable_frame, textvariable=var, font=("Segoe UI", 10))
            return {'widget': entry, 'type': 'basic', 'var': var}


    def _create_buttons(self):
        btn_frame = tb.Frame(self.dlg)
        btn_frame.pack(fill="x", padx=20, pady=10)

        tb.Button(
            btn_frame,
            text="💾 Зберегти",
            bootstyle="success",
            command=self._save,
            width=12
        ).pack(side="left", padx=5)

        tb.Button(
            btn_frame,
            text="❌ Скасувати",
            bootstyle="secondary",
            command=self.dlg.destroy,
            width=12
        ).pack(side="right", padx=5)


    def _get_field_value(self, field_info, field_name):
        try:
            widget = field_info['widget']
            field_type = field_info['type']
            coltype = field_info['coltype']

            if field_type == 'password':
                for child in widget.winfo_children():
                    if isinstance(child, tb.Entry):
                        value = child.get().strip()
                        break
                else:
                    value = ""
                if value:
                    return generate_password_hash(value)
                return None

            elif field_type in ['foreign_key', 'enum', 'year', 'basic', 'numeric', 'date']:
                value = field_info['var'].get().strip()

            elif field_type == 'text':
                value = widget.get("1.0", "end-1c").strip()

            else:
                value = ""

            if not value:
                return None

            if field_type == 'foreign_key':
                if ' - ' in value:
                    first_part = value.split(' - ')[0].strip()
                    if first_part.isdigit():
                        return int(first_part)
                elif value.isdigit():
                    return int(value)
                return None

            if "int" in coltype.lower():
                return int(value) if value else 0
            elif "decimal" in coltype.lower() or "float" in coltype.lower():
                return float(value) if value else 0.0
            elif "year" in coltype.lower():
                return int(value) if value else datetime.datetime.now().year
            else:
                return value

        except (ValueError, TypeError) as e:
            print(f"Помилка конвертації значення для поля {field_name}: {e}")
            return None


    def _save(self):
        try:
            data = {}

            for field_name, field_info in self.field_widgets.items():
                value = self._get_field_value(field_info, field_name)

                if field_info['required'] and value is None:
                    messagebox.showerror("Помилка", f"Поле '{field_name}' обов'язкове")
                    return

                data[field_name] = value

            filtered_data = {k: v for k, v in data.items() if v is not None}

            if not filtered_data:
                messagebox.showwarning("Помилка", "Немає даних для збереження")
                return

            if self.is_purchases:
                if not self._validate_and_adjust_purchases(filtered_data):
                    return

            if self.on_save:
                self.on_save(filtered_data, self.mode)

            self.dlg.destroy()
            messagebox.showinfo("Успіх", "Дані успішно збережено!")

        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка збереження: {str(e)}")


    def _attach_purchases_logic(self, field, field_info):
        if not self.is_purchases:
            return

        var = field_info.get('var')
        if not isinstance(var, tb.StringVar):
            return

        if field == "country_id":
            var.trace_add("write", self._on_country_change)

        if field in ("location_id", "purchase_date"):
            var.trace_add("write", self._on_location_or_date_change)

        if field == "status_id":
            var.trace_add("write", self._on_status_change)

    def _init_purchases_relations(self):
        try:
            if "country_id" in self.field_widgets and "location_id" in self.field_widgets:
                self._on_country_change()

            self._recalculate_estimated_arrival()

            if "status_id" in self.field_widgets:
                self._on_status_change()

        except Exception as e:
            print("init_purchases_relations error:", e)

    def _ensure_status_key_map(self):
        if self._status_key_map is not None:
            return

        self._status_key_map = {}
        try:
            cur = self.parent.conn.cursor()
            cur.execute("SELECT status_id, status_key FROM statuses")
            for sid, skey in cur.fetchall():
                self._status_key_map[str(skey)] = int(sid)
        except Exception as e:
            print("status_key_map error:", e)
            self._status_key_map = {
                "in_ukraine": 9,
                "in_klaipeda": 6
            }

    def _get_status_id_by_key(self, key, default=None):
        self._ensure_status_key_map()
        return self._status_key_map.get(key, default)


    def _on_country_change(self, *args):
        if not self.is_purchases:
            return

        try:
            if "country_id" not in self.field_widgets or "location_id" not in self.field_widgets:
                return

            country_var = self.field_widgets["country_id"]["var"]
            country_str = country_var.get().strip()
            if not country_str:
                return

            country_id_part = country_str.split(" - ")[0].strip()
            if not country_id_part.isdigit():
                return
            country_id = int(country_id_part)

            cur = self.parent.conn.cursor()
            cur.execute(
                """
                SELECT location_id, location_name
                FROM locations
                WHERE country_id = %s
                ORDER BY location_name
                """,
                (country_id,)
            )
            rows = cur.fetchall()

            loc_info = self.field_widgets["location_id"]
            loc_combo = loc_info["widget"]
            loc_var = loc_info["var"]

            new_values = [f"{row[0]} - {row[1]}" for row in rows]
            loc_combo['values'] = new_values

            current_val = loc_var.get()
            if self.mode == "add":
                if new_values:
                    loc_var.set(new_values[0])
            else:
                if current_val not in new_values and new_values:
                    loc_var.set(new_values[0])

            self._recalculate_estimated_arrival()

        except Exception as e:
            print("on_country_change error:", e)

    def _on_location_or_date_change(self, *args):
        if not self.is_purchases:
            return
        self._recalculate_estimated_arrival()

    def _recalculate_estimated_arrival(self):
        if not self.is_purchases:
            return

        try:
            if "purchase_date" not in self.field_widgets:
                return
            if "location_id" not in self.field_widgets:
                return
            if "estimated_arrival_date" not in self.field_widgets:
                return

            purchase_str = self.field_widgets["purchase_date"]["var"].get().strip()
            if not purchase_str:
                return

            try:
                purchase_date = datetime.datetime.strptime(purchase_str, "%Y-%m-%d").date()
            except ValueError:
                return

            loc_var = self.field_widgets["location_id"]["var"]
            loc_str = loc_var.get().strip()
            if not loc_str or " - " not in loc_str:
                return

            loc_id_part = loc_str.split(" - ")[0].strip()
            if not loc_id_part.isdigit():
                return
            location_id = int(loc_id_part)

            cur = self.parent.conn.cursor()
            cur.execute(
                """
                SELECT days_to_port, default_port_id
                FROM locations
                WHERE location_id = %s
                """,
                (location_id,)
            )
            loc_row = cur.fetchone()
            if not loc_row:
                return

            days_to_port, default_port_id = loc_row

            cur.execute(
                """
                SELECT delivery_to_europe_days
                FROM ports
                WHERE port_id = %s
                """,
                (default_port_id,)
            )
            port_row = cur.fetchone()
            if not port_row:
                delivery_days = 0
            else:
                delivery_days = port_row[0]

            total_days = int(days_to_port) + int(delivery_days) + 7
            arrival_date = purchase_date + datetime.timedelta(days=total_days)

            self.field_widgets["estimated_arrival_date"]["var"].set(
                arrival_date.strftime("%Y-%m-%d")
            )

        except Exception as e:
            print("recalculate_estimated_arrival error:", e)

    def _on_status_change(self, *args):
        if not self.is_purchases:
            return

        try:
            if "status_id" not in self.field_widgets or "is_delivered" not in self.field_widgets:
                return

            status_var = self.field_widgets["status_id"]["var"]
            status_str = status_var.get().strip()
            if not status_str or " - " not in status_str:
                return

            status_id_part = status_str.split(" - ")[0].strip()
            if not status_id_part.isdigit():
                return
            status_id = int(status_id_part)

            self._ensure_status_key_map()
            in_ua_id = self._get_status_id_by_key("in_ukraine", 9)
            in_klaipeda_id = self._get_status_id_by_key("in_klaipeda", 6)

            delivered_var = self.field_widgets["is_delivered"]["var"]

            if status_id == in_ua_id:
                delivered_var.set("1")
            elif status_id == in_klaipeda_id:
                delivered_var.set("0")
            else:
                delivered_var.set("0")

        except Exception as e:
            print("on_status_change error:", e)


    def _validate_and_adjust_purchases(self, data: dict) -> bool:
        try:
            cur = self.parent.conn.cursor()

            vin = data.get("vin_number")
            if vin:
                if self.mode == "add":
                    cur.execute(
                        "SELECT purchase_id FROM purchases WHERE vin_number = %s",
                        (vin,)
                    )
                else:
                    cur.execute(
                        """
                        SELECT purchase_id FROM purchases
                        WHERE vin_number = %s AND purchase_id <> %s
                        """,
                        (vin, self.data.get("purchase_id", 0))
                    )
                row = cur.fetchone()
                if row:
                    messagebox.showerror(
                        "Помилка",
                        f"VIN '{vin}' вже використовується в іншій покупці."
                    )
                    return False

            purchase_str = data.get("purchase_date")
            arrival_str = data.get("estimated_arrival_date")

            if purchase_str:
                try:
                    pdate = datetime.datetime.strptime(purchase_str, "%Y-%m-%d").date()
                except ValueError:
                    messagebox.showerror("Помилка", "Невірний формат дати покупки.")
                    return False

                if pdate > datetime.date.today():
                    messagebox.showerror(
                        "Помилка",
                        "Дата покупки не може бути в майбутньому."
                    )
                    return False

                if arrival_str:
                    try:
                        adate = datetime.datetime.strptime(arrival_str, "%Y-%m-%d").date()
                    except ValueError:
                        messagebox.showerror(
                            "Помилка",
                            "Невірний формат дати прибуття."
                        )
                        return False

                    if adate < pdate:
                        messagebox.showerror(
                            "Помилка",
                            "Дата прибуття не може бути раніше дати покупки."
                        )
                        return False

            status_id = data.get("status_id")
            is_delivered = data.get("is_delivered")

            self._ensure_status_key_map()
            in_ua_id = self._get_status_id_by_key("in_ukraine", 9)
            in_klaipeda_id = self._get_status_id_by_key("in_klaipeda", 6)

            if status_id == in_ua_id:
                data["is_delivered"] = 1

            return True

        except Exception as e:
            print("validate_purchases error:", e)
            messagebox.showerror("Помилка", f"Помилка валідації purchases: {e}")
            return False
