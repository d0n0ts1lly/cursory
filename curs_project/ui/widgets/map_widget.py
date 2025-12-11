import os
import math
from PIL import Image, ImageTk
from tkinter import Canvas
import ttkbootstrap as tb
from ttkbootstrap.constants import *
from config import CANVAS_WIDTH, CANVAS_HEIGHT, ASSETS_DIR


class MapWidget(tb.Frame):
    def __init__(self, parent, purchase_data):
        super().__init__(parent)
        self.purchase_data = purchase_data or {}
        self.zoom_factor = 1.0
        self.min_zoom = 0.6
        self.max_zoom = 1.8
        self.glow_phase = 0.0
        self.moving_phase = 0.0
        self._animation_job = None
        self.base_map_image = self._load_base_map()
        self.map_photo = None
        self._map_photo_zoom = None
        self.coords = self._build_coords()
        self._create_widgets()
        self._draw_map()
        self._start_glow_animation()

    def _create_widgets(self):
        title = tb.Label(self, text="Маршрут доставки",
                         font=("Segoe UI", 12, "bold"))
        title.pack(pady=(5, 0))

        self.map_canvas = Canvas(
            self,
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT,
            bg="#F2F2F7",
            highlightthickness=1,
            highlightbackground="#D1D1D6"
        )
        self.map_canvas.pack(fill="both", expand=True, padx=8, pady=(6, 4))

        zoom_frame = tb.Frame(self)
        zoom_frame.pack(pady=(0, 6))

        tb.Button(
            zoom_frame, text="−", width=3,
            bootstyle="secondary-outline", command=self.zoom_out
        ).pack(side=LEFT, padx=2)

        tb.Button(
            zoom_frame, text="100%", width=6,
            bootstyle="light-outline", command=self.reset_zoom
        ).pack(side=LEFT, padx=2)

        tb.Button(
            zoom_frame, text="+", width=3,
            bootstyle="secondary", command=self.zoom_in
        ).pack(side=LEFT, padx=2)

    def update_purchase(self, purchase_data):
        self.purchase_data = purchase_data or {}
        self._draw_map()

    def _build_coords(self):
        return {
            "Маямі (США)": (183, 148),
            "Лос-ААнджелес (США)": (135, 181),
            "Токіо (Японія)": (640, 170),
            "Шанхай (Китай)": (639, 182),
            "Берлін (Німеччина)": (376, 124),
            "Варшава (Польща)": (400, 115),
            "Вільнюс (Литва)": (415, 96),
            "Baltimore": (170, 157),
            "Hamburg": (377, 108),
            "Gdynia": (394, 108),
            "Klaipėda": (411, 93),
            "Україна": (427, 124)
        }

    def _resolve_coord_key(self, name):
        if not name:
            return None
        name = name.strip()
        if name in self.coords:
            return name
        base = name.split("(")[0].strip()
        for key in self.coords:
            if base in key:
                return key
        for key in self.coords:
            if key in name:
                return key
        return None

    def _load_base_map(self):
        possible = [
            os.path.join(ASSETS_DIR, "world_map.png"),
            "world_map.png",
            "assets/world_map.png",
        ]
        for p in possible:
            if os.path.exists(p):
                try:
                    return Image.open(p).convert("RGBA")
                except:
                    pass
        return None

    def _update_map_photo_for_zoom(self):
        if not self.base_map_image:
            return
        if self._map_photo_zoom == self.zoom_factor and self.map_photo:
            return
        w = int(CANVAS_WIDTH * self.zoom_factor)
        h = int(CANVAS_HEIGHT * self.zoom_factor)
        img = self.base_map_image.resize((w, h), Image.Resampling.LANCZOS)
        self.map_photo = ImageTk.PhotoImage(img)
        self._map_photo_zoom = self.zoom_factor

    def _build_route(self):
        loc = self._resolve_coord_key(self.purchase_data.get("location_name"))
        port = self._resolve_coord_key(self.purchase_data.get("port_name"))
        ua = "Україна"
        status = int(self.purchase_data.get("status_id", 1))
        EUROPE = {"Берлін (Німеччина)", "Варшава (Польща)", "Вільнюс (Литва)"}

        if not loc or loc not in self.coords:
            return {}, [], None, None, None

        points = {"start": self.coords[loc], "ua": self.coords[ua]}
        segments = []
        active_point = None
        active_segment = None
        car_position = None

        if loc in EUROPE:
            segments.append(("start", "ua"))
            if status in (1, 2):
                active_point = "start"
            elif status in (3, 4, 5, 6, 7, 8):
                active_segment = ("start", "ua")
                car_position = ("start", "ua")
            elif status == 9:
                active_point = "ua"
            return points, segments, active_point, active_segment, car_position

        if port in self.coords:
            points["port"] = self.coords[port]
            segments.append(("start", "port"))
            segments.append(("port", "klaipeda"))
        else:
            segments.append(("start", "klaipeda"))

        points["klaipeda"] = self.coords["Klaipėda"]
        segments.append(("klaipeda", "ua"))

        if status in (1, 2):
            active_point = "start"
        elif status == 3:
            active_segment = ("start", "port") if port else ("start", "klaipeda")
            car_position = active_segment
        elif status == 4:
            active_point = "port" if port else None
        elif status == 5:
            s = ("port", "klaipeda") if port else ("start", "klaipeda")
            active_segment = s
            car_position = s
        elif status == 6:
            active_point = "klaipeda"
        elif status in (7, 8):
            active_segment = ("klaipeda", "ua")
            car_position = ("klaipeda", "ua")
        elif status == 9:
            active_point = "ua"

        return points, segments, active_point, active_segment, car_position

    def _draw_map(self):
        self.map_canvas.delete("all")
        self._update_map_photo_for_zoom()
        if self.map_photo:
            self.map_canvas.create_image(
                CANVAS_WIDTH//2,
                CANVAS_HEIGHT//2,
                image=self.map_photo
            )

        points, segments, active_point, active_segment, car_pos = self._build_route()

        LINE_COLOR = "#4A90E2"
        LINE_ACTIVE = "#0A84FF"
        POINT_BORDER = "#0A84FF"
        POINT_FILL = "#FFFFFF"
        POINT_ACTIVE = "#FFD60A"
        CAR_COLOR = "#FF9F0A"

        base_r = 4 * self.zoom_factor

        for (s, e) in segments:
            if s not in points or e not in points:
                continue
            x1, y1 = self._scale_point(*points[s])
            x2, y2 = self._scale_point(*points[e])
            is_active = active_segment == (s, e)
            self.map_canvas.create_line(
                x1, y1, x2, y2,
                fill=LINE_ACTIVE if is_active else LINE_COLOR,
                width=2,
                smooth=True
            )

        if car_pos:
            (s, e) = car_pos
            if s in points and e in points:
                x1, y1 = self._scale_point(*points[s])
                x2, y2 = self._scale_point(*points[e])
                px = (x1 + x2) / 2
                py = (y1 + y2) / 2
                r = 5 * self.zoom_factor + 2 * math.sin(self.moving_phase)
                self.map_canvas.create_oval(
                    px - r, py - r,
                    px + r, py + r,
                    fill=CAR_COLOR,
                    outline=""
                )

        for pid, (xx, yy) in points.items():
            sx, sy = self._scale_point(xx, yy)
            is_active_p = (pid == active_point)
            if is_active_p:
                phase = (math.sin(self.glow_phase) + 1) / 2
                glow_r = base_r * (3.0 + 0.4 * phase)
                self.map_canvas.create_oval(
                    sx - glow_r, sy - glow_r,
                    sx + glow_r, sy + glow_r,
                    outline="#FFE066",
                    width=2
                )

            self.map_canvas.create_oval(
                sx - base_r, sy - base_r,
                sx + base_r, sy + base_r,
                outline=POINT_BORDER,
                width=2,
                fill=POINT_FILL
            )

            self.map_canvas.create_oval(
                sx - base_r*0.6, sy - base_r*0.6,
                sx + base_r*0.6, sy + base_r*0.6,
                fill=POINT_ACTIVE if is_active_p else POINT_BORDER,
                outline=""
            )

    def _start_glow_animation(self):
        if not self._animation_job:
            self._animate()

    def _animate(self):
        self.glow_phase += 0.2
        self.moving_phase += 0.3
        self._draw_map()
        self._animation_job = self.after(70, self._animate)

    def _scale_point(self, x, y):
        cx, cy = CANVAS_WIDTH / 2, CANVAS_HEIGHT / 2
        f = self.zoom_factor
        return cx + (x - cx) * f, cy + (y - cy) * f

    def zoom_in(self):
        self.zoom_factor = min(self.max_zoom, self.zoom_factor + 0.15)
        self._update_map_photo_for_zoom()
        self._draw_map()

    def zoom_out(self):
        self.zoom_factor = max(self.min_zoom, self.zoom_factor - 0.15)
        self._update_map_photo_for_zoom()
        self._draw_map()

    def reset_zoom(self):
        self.zoom_factor = 1.0
        self._update_map_photo_for_zoom()
        self._draw_map()
