import datetime
import os
import io
import urllib.request
import ssl
from PIL import Image, ImageTk
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from config import ASSETS_DIR


PHOTO_WIDTH = 260
PHOTO_HEIGHT = 160


class CarCard(tb.Frame):
    def __init__(self, parent, car_data, on_click=None):
        super().__init__(parent, padding=5)

        self.car_data = car_data
        self.on_click = on_click

        self.card = tb.Frame(
            self,
            padding=10,
            borderwidth=1,
            relief="solid"
        )
        self.card.pack(fill="x", expand=True, pady=5)

        self.card.bind("<Enter>", lambda e: self._hover(True))
        self.card.bind("<Leave>", lambda e: self._hover(False))

        self._create_card()

        if on_click:
            self.card.bind("<Button-1>", lambda e: on_click(car_data))
            for child in self.card.winfo_children():
                child.bind("<Button-1>", lambda e: on_click(car_data))

    def _hover(self, active):
        self.card.configure(borderwidth=2 if active else 1)

    def _create_card(self):

        image_frame = tb.Frame(
            self.card,
            padding=4,
            borderwidth=1,
            relief="ridge",
            width=PHOTO_WIDTH,
            height=PHOTO_HEIGHT
        )
        image_frame.pack(fill="x", pady=(0, 8))
        image_frame.pack_propagate(False)

        image_path = self.car_data.get("first_image_path")
        has_images = self.car_data.get("has_images", False)

        ok = self._try_load_image(image_frame, image_path)
        if not ok:
            self._show_placeholder(image_frame)

        info = tb.Frame(self.card)
        info.pack(fill="x")

        title = f"{self.car_data.get('car_make', '')} {self.car_data.get('car_model', '')}"
        tb.Label(info, text=title, font=("Segoe UI", 12, "bold")).pack(anchor="w")

        tb.Label(info, text=f"Рік: {self.car_data.get('car_year', 'N/A')}",
                 font=("Segoe UI", 9)).pack(anchor="w", pady=2)

        vin = self.car_data.get("vin_number", "N/A")
        short_vin = f"{vin[:8]}...{vin[-4:]}" if len(str(vin)) > 12 else vin
        tb.Label(info, text=f"VIN: {short_vin}",
                 font=("Segoe UI", 8),
                 bootstyle="secondary").pack(anchor="w", pady=2)

        price = self.car_data.get("price_usd", 0)
        tb.Label(info, text=f"${price:,.2f}",
                 font=("Segoe UI", 12, "bold"),
                 bootstyle="success").pack(anchor="w", pady=4)

        status = self.car_data.get("status_name", "Невідомо")
        color = "success" if "україні" in status.lower() else "warning"
        tb.Label(info, text=status,
                 font=("Segoe UI", 8, "bold"),
                 bootstyle=color,
                 padding=4).pack(anchor="w", pady=4)

        self._add_days_counter()

    def _try_load_image(self, parent, image_path):
        if not image_path:
            return False

        try:
            if os.path.exists(image_path):
                pil = Image.open(image_path)
            elif image_path.startswith(("http://", "https://")):
                req = urllib.request.Request(image_path, headers={"User-Agent": "Mozilla/5.0"})
                ctx = ssl._create_unverified_context()
                data = urllib.request.urlopen(req, timeout=15, context=ctx).read()
                pil = Image.open(io.BytesIO(data))
            else:
                alt = os.path.join(ASSETS_DIR, image_path)
                if os.path.exists(alt):
                    pil = Image.open(alt)
                else:
                    return False

            pil.thumbnail((PHOTO_WIDTH, PHOTO_HEIGHT), Image.Resampling.LANCZOS)

            photo = ImageTk.PhotoImage(pil)

            lbl = tb.Label(parent, image=photo)
            lbl.image = photo
            lbl.pack(expand=True)

            return True

        except Exception as e:
            print("Ошибка загрузки изображения:", e)
            return False

    def _show_placeholder(self, parent):
        placeholder = os.path.join(ASSETS_DIR, "placeholder.jpg")

        try:
            if os.path.exists(placeholder):
                pil = Image.open(placeholder)
                pil.thumbnail((PHOTO_WIDTH, PHOTO_HEIGHT), Image.Resampling.LANCZOS)

                photo = ImageTk.PhotoImage(pil)
                lbl = tb.Label(parent, image=photo)
                lbl.image = photo
                lbl.pack(expand=True)

                tb.Label(parent, text="Фото відсутнє", font=("Segoe UI", 8),
                         bootstyle="secondary").pack(pady=2)
                return
        except:
            pass

        wrapper = tb.Frame(parent)
        wrapper.pack(expand=True, fill="both")

        tb.Label(wrapper, text="🚗", font=("Segoe UI", 42)).pack(expand=True)
        tb.Label(wrapper, text="Немає фото",
                 font=("Segoe UI", 8),
                 bootstyle="secondary").pack()

    def _add_days_counter(self):
        try:
            est = self.car_data.get("estimated_arrival_date")
            status = self.car_data.get("status_name", "").lower()

            if not est:
                return

            if isinstance(est, str):
                est = datetime.datetime.strptime(est, "%Y-%m-%d").date()

            today = datetime.date.today()
            delivered = "україні" in status or self.car_data.get("is_delivered", False)

            if delivered:
                diff = (today - est).days
                txt = f"Прибув {diff} дн. тому" if diff >= 0 else f"До прибуття: {abs(diff)} дн."
                color = "success" if diff >= 0 else "warning"
            else:
                if est < today:
                    diff = (today - est).days
                    txt = f"⚠️ Запізнення: {diff} дн."
                    color = "danger"
                else:
                    diff = (est - today).days
                    txt = f"До прибуття: {diff} дн."
                    color = "warning" if diff > 7 else "success"

            tb.Label(
                self.card,
                text=txt,
                font=("Segoe UI", 8, "bold"),
                bootstyle=color,
                padding=4
            ).pack(anchor="w", pady=4)

        except Exception as e:
            print("Помилка розрахунку днів:", e)
