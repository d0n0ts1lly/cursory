import datetime
import ttkbootstrap as tb
from ttkbootstrap.constants import *

class CalendarDialog:
    def __init__(self, parent, title="Виберіть дату"):
        self.parent = parent
        self.result = None
        
        self.dialog = tb.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("500x350")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 500) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 350) // 2
        self.dialog.geometry(f"+{x}+{y}")
        
        self.current_date = datetime.datetime.now()
        self.selected_date = self.current_date
        
        self._create_widgets()
        self._update_calendar()
        
    def _create_widgets(self):
        header_frame = tb.Frame(self.dialog)
        header_frame.pack(fill="x", padx=10, pady=10)
        
        self.month_year_var = tb.StringVar()
        self.month_year_label = tb.Label(header_frame, textvariable=self.month_year_var, 
                                       font=("Segoe UI", 12, "bold"))
        self.month_year_label.pack(side="left", expand=True)
        
        tb.Button(header_frame, text="◀", width=3,
                 command=self._prev_month).pack(side="left", padx=2)
        tb.Button(header_frame, text="▶", width=3,
                 command=self._next_month).pack(side="left", padx=2)
        
        days_frame = tb.Frame(self.dialog)
        days_frame.pack(fill="x", padx=10, pady=5)
        
        days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Нд"]
        for day in days:
            lbl = tb.Label(days_frame, text=day, width=4, font=("Segoe UI", 9, "bold"))
            lbl.pack(side="left")
        
        self.calendar_frame = tb.Frame(self.dialog)
        self.calendar_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        btn_frame = tb.Frame(self.dialog)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        tb.Button(btn_frame, text="Сьогодні", bootstyle="secondary",
                 command=self._set_today).pack(side="left", padx=5)
        tb.Button(btn_frame, text="OK", bootstyle="success",
                 command=self._ok).pack(side="right", padx=5)
        tb.Button(btn_frame, text="Скасувати", bootstyle="danger",
                 command=self.dialog.destroy).pack(side="right", padx=5)
    
    def _update_calendar(self):
        for widget in self.calendar_frame.winfo_children():
            widget.destroy()
        
        month_names = [
            "Січень", "Лютий", "Березень", "Квітень", "Травень", "Червень",
            "Липень", "Серпень", "Вересень", "Жовтень", "Листопад", "Грудень"
        ]
        self.month_year_var.set(f"{month_names[self.current_date.month-1]} {self.current_date.year}")
        
        first_day = self.current_date.replace(day=1)
        weekday = first_day.weekday()  # Пн = 0
        
        if self.current_date.month == 12:
            next_month = self.current_date.replace(year=self.current_date.year+1, month=1, day=1)
        else:
            next_month = self.current_date.replace(month=self.current_date.month+1, day=1)
        days_in_month = (next_month - datetime.timedelta(days=1)).day
        
        row, col = 0, 0
        
        for i in range(weekday):
            lbl = tb.Label(self.calendar_frame, text="", width=4)
            lbl.grid(row=row, column=col, padx=2, pady=2)
            col += 1
        
        for day in range(1, days_in_month + 1):
            date = self.current_date.replace(day=day)
            is_today = date.date() == datetime.datetime.now().date()
            is_selected = date.date() == self.selected_date.date()

            # 🎨 Правильная логика выделения:
            if is_selected:
                btn_style = "info"       # выбранная дата = яркая
            elif is_today:
                btn_style = "secondary"  # сегодня = серый (если не выбрано)
            else:
                btn_style = "default"    # обычные дни

            btn = tb.Button(
                self.calendar_frame,
                text=str(day),
                width=4,
                bootstyle=btn_style,
                command=lambda d=date: self._select_date(d)
            )
            btn.grid(row=row, column=col, padx=2, pady=2)
            
            col += 1
            if col > 6:
                col = 0
                row += 1
    
    def _prev_month(self):
        if self.current_date.month == 1:
            self.current_date = self.current_date.replace(year=self.current_date.year-1, month=12)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month-1)
        self._update_calendar()
    
    def _next_month(self):
        if self.current_date.month == 12:
            self.current_date = self.current_date.replace(year=self.current_date.year+1, month=1)
        else:
            self.current_date = self.current_date.replace(month=self.current_date.month+1)
        self._update_calendar()
    
    def _set_today(self):
        self.selected_date = datetime.datetime.now()
        self.current_date = self.selected_date
        self._update_calendar()
    
    def _select_date(self, date):
        self.selected_date = date
        self._update_calendar()
    
    def _ok(self):
        self.result = self.selected_date.strftime("%Y-%m-%d")
        self.dialog.destroy()
    
    def show(self):
        self.dialog.wait_window()
        return self.result
