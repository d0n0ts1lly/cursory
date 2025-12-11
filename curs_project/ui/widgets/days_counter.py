import datetime
import ttkbootstrap as tb
from ttkbootstrap.constants import *


class DaysCounterWidget(tb.Frame):
    def __init__(self, parent, purchase_data):
        super().__init__(parent, padding=12)
        self.purchase_data = purchase_data
        
        style = tb.Style()
        self.bg = style.colors.bg
        self.fg = style.colors.fg
        self.border = style.colors.border   
        if self.border is None:
            self.border = "#888888"

        self._create_widget()
        self._calculate_days()
    
    def _create_widget(self):
        header = tb.Frame(self, padding=8)
        header.pack(fill="x")

        tb.Label(
            header,
            text=f"🚗 {self.purchase_data.get('car_make', '')} {self.purchase_data.get('car_model', '')}",
            font=("Segoe UI", 12, "bold")
        ).pack(anchor="w")

        tb.Label(
            header,
            text=f"VIN: {self.purchase_data.get('vin_number', '')}",
            font=("Segoe UI", 9),
            bootstyle="secondary"
        ).pack(anchor="w", pady=(2, 0))

        self.days_frame = tb.LabelFrame(
            self,
            text="Статус доставки",
            bootstyle="info",
            padding=12
        )
        self.days_frame.pack(fill="x", pady=10)

        self.days_label = tb.Label(
            self.days_frame,
            text="",
            font=("Segoe UI", 14, "bold")
        )
        self.days_label.pack()

        status_container = tb.Frame(self, padding=6)
        status_container.pack(fill="x")

        tb.Label(
            status_container,
            text="Статус:",
            font=("Segoe UI", 10, "bold")
        ).pack(side="left")

        status_name = self.purchase_data.get("status_name", "Невідомо")
        status_color = "success" if "україні" in status_name.lower() else "warning"

        tb.Label(
            status_container,
            text=status_name,
            bootstyle=status_color,
            font=("Segoe UI", 10, "bold")
        ).pack(side="left", padx=8)

    def _calculate_days(self):
        try:
            est_date = self.purchase_data.get("estimated_arrival_date")
            status_name = self.purchase_data.get("status_name", "").lower()

            if not est_date:
                self.days_label.config(text="Дата прибуття не вказана")
                return

            if isinstance(est_date, str):
                est_date = datetime.datetime.strptime(est_date, "%Y-%m-%d").date()

            today = datetime.date.today()

            delivered = "україні" in status_name or self.purchase_data.get("is_delivered", False)

            if delivered:
                days_passed = (today - est_date).days
                if days_passed >= 0:
                    self.days_label.config(text=f"Прибув {days_passed} дн. тому")
                    self.days_frame.configure(bootstyle="success")
                else:
                    self.days_label.config(text=f"До прибуття: {abs(days_passed)} дн.")
                    self.days_frame.configure(bootstyle="warning")
                return

            if est_date < today:
                days_late = (today - est_date).days
                self.days_label.config(text=f"⚠️ Запізнення: {days_late} дн.")
                self.days_frame.configure(bootstyle="danger")
            else:
                days_left = (est_date - today).days
                self.days_label.config(text=f"До прибуття: {days_left} дн.")

                if days_left > 7:
                    self.days_frame.configure(bootstyle="warning")
                else:
                    self.days_frame.configure(bootstyle="success")

        except Exception as e:
            print(f"Помилка розрахунку днів: {e}")
            self.days_label.config(text="Помилка розрахунку")
