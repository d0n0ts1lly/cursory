import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox
from PIL import Image, ImageTk
import os

from config.settings import Config
from core.auth import AuthManager
from views.login import LoginView
from views.admin.dashboard import AdminDashboard
from views.admin.crud import AdminCRUDView
from views.user.dashboard import UserDashboard
from views.user.cars import CarManager
from views.components.map import MapManager
from utils.image_processing import load_image_safe, create_round_avatar
from mysql.connector import Error

class EnhancedAutoTrackerApp(tb.Window):
    def __init__(self):
        super().__init__(themename=Config.DEFAULT_THEME)
        self.title("Auto Tracker Pro — Advanced Vehicle Tracking")
        self.geometry(f"{Config.WINDOW_WIDTH}x{Config.WINDOW_HEIGHT}")
        self.minsize(Config.MIN_WINDOW_WIDTH, Config.MIN_WINDOW_HEIGHT)

        self.auth_manager = AuthManager()
        self.conn = None
        self.current_user = None
        self.dark_mode = False

        # UI containers
        self.left_frame = None
        self.center_frame = None
        self.right_frame = None

        # Managers
        self.map_manager = None
        self.admin_crud = None
        self.car_manager = None
        
        # UI widgets
        self.cars_list = None
        self.map_canvas = None

        # Data caches
        self.user_cars = []
        self.notifications = []

        # Current views
        self.current_admin_dashboard = None
        self.current_user_dashboard = None

        # Build login-first UI
        self._build_login_ui()

    def _build_login_ui(self):
        """Построение UI входа"""
        self.login_view = LoginView(self, self.auth_manager, self._on_login_success)

    def _on_login_success(self, user, connection):
        """Обработка успешного входа"""
        self.current_user = user
        self.conn = connection
        self.map_manager = MapManager(self, self.conn)
        self.admin_crud = AdminCRUDView(self, self.conn)
        self.car_manager = CarManager(self, self.conn, self.current_user)
        
        self._load_notifications()
        self._build_main_ui()

    def _build_main_ui(self):
        """Построение основного UI"""
        for w in self.winfo_children():
            w.destroy()

        self._create_top_bar()
        self._create_main_content()

    def _create_top_bar(self):
        """Создает верхнюю панель с пользовательской информацией"""
        topbar = tb.Frame(self, bootstyle="dark")
        topbar.pack(fill="x", padx=0, pady=0)

        # Left side - app info
        left_info = tb.Frame(topbar, bootstyle="dark")
        left_info.pack(side="left", padx=15, pady=8)
        
        tb.Label(left_info, text="🚗 Auto Tracker Pro", font=("Segoe UI", 14, "bold"), 
                bootstyle="inverse-dark").pack(side="left")
        
        # Center - user info
        user_info = tb.Frame(topbar, bootstyle="dark")
        user_info.pack(side="left", padx=20, pady=8)
        
        tb.Label(user_info, text=f"Вітаємо, {self.current_user['username']}", 
                font=("Segoe UI", 11, "bold"), bootstyle="inverse-dark").pack(side="left")
        tb.Label(user_info, text=f"• Роль: {self.current_user['role']}", 
                bootstyle="inverse-dark").pack(side="left", padx=10)

        # Right side - controls
        controls = tb.Frame(topbar, bootstyle="dark")
        controls.pack(side="right", padx=15, pady=8)

        # Notifications button with badge
        notification_btn = tb.Button(controls, text="🔔", bootstyle="dark-outline",
                                   command=self._show_notifications)
        notification_btn.pack(side="left", padx=5)
        
        # Theme toggle
        theme_btn = tb.Button(controls, text="🌙", bootstyle="dark-outline",
                            command=self._toggle_theme)
        theme_btn.pack(side="left", padx=5)
        
        # Logout button
        logout_btn = tb.Button(controls, text="Вийти", bootstyle="danger-outline",
                             command=self._logout)
        logout_btn.pack(side="left", padx=5)

    def _create_main_content(self):
        """Создает основное содержимое в зависимости от роли"""
        main_container = tb.Frame(self)
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        if self.current_user["role"] == "admin":
            self._build_admin_dashboard(main_container)
        else:
            self._build_user_dashboard(main_container)

    def _build_admin_dashboard(self, parent):
        """Построение админской панели"""
        self.current_admin_dashboard = AdminDashboard(parent, self.conn, self.current_user)
        
        # Переопределяем методы навигации
        self.current_admin_dashboard._admin_navigate = self._admin_navigate
        self.current_admin_dashboard._admin_open_table = self._admin_open_table
        self.current_admin_dashboard._show_analytics = self._show_analytics

    def _build_user_dashboard(self, parent):
        """Построение пользовательской панели"""
        self.current_user_dashboard = UserDashboard(parent, self.conn, self.current_user)
        
        # Переопределяем методы
        self.current_user_dashboard._add_new_car = self._add_new_car
        self.current_user_dashboard._show_detailed_info = self._show_detailed_info
        self.current_user_dashboard._export_my_data = self._export_my_data
        
        # Создаем карту
        self.map_canvas = self.map_manager.create_map_canvas(self.current_user_dashboard.map_container)
        
        # Устанавливаем callback для выбора автомобиля
        self.current_user_dashboard.parent.on_car_select = self._on_car_select

    # ------------------ ADMIN METHODS ------------------
    def _admin_navigate(self, destination):
        """Навигация в админ-панели"""
        for w in self.current_admin_dashboard.center_frame.winfo_children():
            w.destroy()

        if destination == "dashboard":
            self.current_admin_dashboard._build_admin_main()
        elif destination == "analytics":
            self._show_analytics()
        elif destination == "map_management":
            self._show_map_management()
        else:
            self._admin_open_table(destination)

    def _admin_open_table(self, table):
        """Открытие таблицы для админа"""
        self.admin_crud.open_table(table)

    def _show_analytics(self):
        """Показ аналитики"""
        analytics_frame = tb.Frame(self.current_admin_dashboard.center_frame)
        analytics_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tb.Label(analytics_frame, text="📊 Аналітика та звіти", 
                font=("Segoe UI", 18, "bold")).pack(pady=10)

        # Статистика по статусам доставки
        try:
            cur = self.conn.cursor()
            cur.execute("""
                SELECT ds.status_name, COUNT(p.purchase_id) as count
                FROM delivery_status ds
                LEFT JOIN purchases p ON ds.status_id = p.delivery_status_id
                GROUP BY ds.status_id, ds.status_name
                ORDER BY ds.order_index
            """)
            status_stats = cur.fetchall()
            cur.close()

            stats_frame = tb.Frame(analytics_frame)
            stats_frame.pack(fill="x", pady=10)

            for status_name, count in status_stats:
                row = tb.Frame(stats_frame)
                row.pack(fill="x", pady=2)
                tb.Label(row, text=status_name, width=20, anchor="w").pack(side="left")
                progress = tb.Progressbar(row, value=count, maximum=max(10, count*2), bootstyle="success")
                progress.pack(side="left", fill="x", expand=True, padx=5)
                tb.Label(row, text=str(count)).pack(side="right")

        except Error as e:
            tb.Label(analytics_frame, text=f"Помилка завантаження аналітики: {e}").pack()

        # Кнопки экспорта
        export_frame = tb.Frame(analytics_frame)
        export_frame.pack(fill="x", pady=20)

        tb.Button(export_frame, text="📄 Експорт в CSV", bootstyle="success",
                 command=self._export_to_csv).pack(side="left", padx=5)
        tb.Button(export_frame, text="📊 Згенерувати звіт", bootstyle="info",
                 command=self._generate_report).pack(side="left", padx=5)

    def _show_map_management(self):
        """Управление картой и контрольными точками"""
        map_frame = tb.Frame(self.current_admin_dashboard.center_frame)
        map_frame.pack(fill="both", expand=True, padx=20, pady=20)

        tb.Label(map_frame, text="🗺️ Управління картою та маршрутами", 
                font=("Segoe UI", 18, "bold")).pack(pady=10)

        # Карта
        map_container = tb.Frame(map_frame)
        map_container.pack(fill="both", expand=True, pady=10)

        self.map_manager.create_map_canvas(map_container)

        # Управление точками
        points_frame = tb.Frame(map_frame)
        points_frame.pack(fill="x", pady=10)

        tb.Button(points_frame, text="➕ Додати точку маршруту", bootstyle="success",
                 command=self._add_route_point).pack(side="left", padx=5)
        tb.Button(points_frame, text="📋 Всі точки маршруту", bootstyle="info",
                 command=lambda: self._admin_open_table("delivery_route_points")).pack(side="left", padx=5)

    def _add_route_point(self):
        """Добавление точки маршрута"""
        def save_point(data, mode):
            try:
                cur = self.conn.cursor()
                if mode == "add":
                    columns = ', '.join([f"`{k}`" for k in data.keys()])
                    placeholders = ', '.join(['%s'] * len(data))
                    sql = f"INSERT INTO delivery_route_points ({columns}) VALUES ({placeholders})"
                    cur.execute(sql, tuple(data.values()))
                self.conn.commit()
                cur.close()
                messagebox.showinfo("Успіх", "Точку маршруту успішно додано!")
            except Error as e:
                messagebox.showerror("Помилка", f"Помилка збереження: {str(e)}")

        from views.components.dialogs import ModernCRUDDialog
        ModernCRUDDialog(self, "Додати точку маршруту", "delivery_route_points", 
                        "add", on_save=save_point)

    # ------------------ USER METHODS ------------------
    def _on_car_select(self, purchase):
        """Обработка выбора автомобиля"""
        if self.current_user_dashboard:
            self.current_user_dashboard.update_car_info(purchase)
            self._show_car_details(purchase)

    def _show_car_details(self, purchase):
        """Показ деталей автомобиля"""
        # Загружаем изображение
        img = self._load_main_image_for_purchase(purchase["purchase_id"])
        self._set_car_image(img)

        # Строим временную шкалу
        self._build_timeline(purchase)

        # Обновляем карту
        self._redraw_map(purchase)

    def _set_car_image(self, pil_img):
        """Установка изображения автомобиля"""
        max_w, max_h = 200, 150
        img = pil_img.copy()
        img.thumbnail((max_w, max_h), Image.LANCZOS)
        self.car_img_tk = ImageTk.PhotoImage(img)
        
        # Создаем круглое изображение для красоты
        round_img = create_round_avatar(pil_img, (120, 120))
        self.car_round_tk = ImageTk.PhotoImage(round_img)
        
        if self.current_user_dashboard and hasattr(self.current_user_dashboard, 'car_image_lbl'):
            self.current_user_dashboard.car_image_lbl.configure(image=self.car_round_tk)

    def _build_timeline(self, purchase):
        """Построение временной шкалы статусов"""
        if not self.current_user_dashboard:
            return
            
        for w in self.current_user_dashboard.timeline_frame.winfo_children():
            w.destroy()

        try:
            cur = self.conn.cursor(dictionary=True)
            cur.execute("SELECT * FROM delivery_status ORDER BY order_index")
            statuses = cur.fetchall() or []
            cur.close()
        except:
            statuses = []

        cur_status_id = purchase.get("delivery_status_id")
        timeline_row = tb.Frame(self.current_user_dashboard.timeline_frame)
        timeline_row.pack(fill="x", padx=10, pady=5)

        for s in statuses:
            sid = s["status_id"]
            name = s["status_name"]
            
            if cur_status_id is not None and s["order_index"] < (self._get_order_index(cur_status_id) or 0):
                style = "success"
            elif cur_status_id is not None and s["order_index"] == (self._get_order_index(cur_status_id) or 0):
                style = "warning"
            else:
                style = "secondary"

            status_frame = tb.Frame(timeline_row, padding=5)
            status_frame.pack(side="left", expand=True)
            
            tb.Label(status_frame, text=name, font=("Segoe UI", 9), 
                    bootstyle=style).pack()
            
            # Индикатор статуса
            indicator = tb.Frame(status_frame, width=20, height=20)
            indicator.pack(pady=2)
            indicator.configure(bootstyle=style)

    def _redraw_map(self, purchase):
        """Перерисовка карты с маршрутом"""
        if not self.map_manager:
            return

        self.map_manager.clear_map()

        if not purchase:
            return

        # Рисуем маршрут для выбранного авто
        self.map_manager.draw_car_route(purchase["purchase_id"])

    def _add_new_car(self):
        """Добавление нового автомобиля"""
        if self.car_manager:
            self.car_manager.add_new_car(self._load_user_cars)

    def _show_detailed_info(self):
        """Показывает детальную информацию о выбранном авто"""
        if not self.current_user_dashboard or not self.current_user_dashboard.cars_list:
            return
            
        sel = self.current_user_dashboard.cars_list.selection()
        if not sel:
            messagebox.showwarning("Увага", "Оберіть авто зі списку")
            return

        purchase_id = int(sel[0])
        purchase = next((p for p in self.current_user_dashboard.user_cars if p["purchase_id"] == purchase_id), None)
        if not purchase:
            return

        if self.car_manager:
            self.car_manager.show_detailed_info(purchase)

    def _export_my_data(self):
        """Экспорт данных пользователя"""
        if self.car_manager:
            self.car_manager.export_user_data(self.current_user['id'])

    # ------------------ UTILITY METHODS ------------------
    def _load_user_cars(self):
        """Загрузка автомобилей пользователя"""
        if self.current_user_dashboard:
            self.current_user_dashboard._load_user_cars()

    def _load_main_image_for_purchase(self, purchase_id):
        """Загрузка основного изображения для покупки"""
        return load_image_safe(Config.DEFAULT_CAR)

    def _get_order_index(self, status_id):
        """Получение порядка статуса"""
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT order_index FROM delivery_status WHERE status_id=%s", (status_id,))
            r = cur.fetchone()
            cur.close()
            return r[0] if r else None
        except:
            return None

    def _load_notifications(self):
        """Загрузка уведомлений пользователя"""
        try:
            cur = self.conn.cursor(dictionary=True)
            cur.execute("""
                SELECT * FROM notifications 
                WHERE user_id = %s AND is_read = FALSE
                ORDER BY created_at DESC
                LIMIT 10
            """, (self.current_user['id'],))
            self.notifications = cur.fetchall()
            cur.close()
        except:
            self.notifications = []

    def _show_notifications(self):
        """Показ уведомлений"""
        if not self.notifications:
            messagebox.showinfo("Сповіщення", "Немає нових сповіщень")
            return

        win = tb.Toplevel(self)
        win.title("Сповіщення")
        win.geometry("400x500")

        for notification in self.notifications:
            frame = tb.Frame(win, padding=10)
            frame.pack(fill="x", padx=10, pady=5)

            tb.Label(frame, text=notification['title'], 
                    font=("Segoe UI", 11, "bold")).pack(anchor="w")
            tb.Label(frame, text=notification['message'], 
                    font=("Segoe UI", 10)).pack(anchor="w")
            tb.Label(frame, text=notification['created_at'].strftime("%d.%m.%Y %H:%M"),
                    font=("Segoe UI", 9), bootstyle="secondary").pack(anchor="w")

    def _toggle_theme(self):
        """Переключение темы"""
        self.dark_mode = not self.dark_mode
        if self.dark_mode:
            self.style.theme_use(Config.DARK_THEME)
        else:
            self.style.theme_use(Config.DEFAULT_THEME)

    def _export_to_csv(self):
        """Экспорт данных в CSV"""
        from utils.helpers import export_to_csv
        export_to_csv(self.conn, "SELECT * FROM purchases", "purchases_export.csv")

    def _generate_report(self):
        """Генерация отчета"""
        try:
            cur = self.conn.cursor()
            
            # Статистика по месяцам
            cur.execute("""
                SELECT DATE_FORMAT(purchase_date, '%Y-%m') as month, 
                       COUNT(*) as count
                FROM purchases 
                GROUP BY month 
                ORDER BY month DESC 
                LIMIT 6
            """)
            monthly_stats = cur.fetchall()
            
            report = "📈 Звіт по відправленням\n\n"
            report += "Останні 6 місяців:\n"
            for month, count in monthly_stats:
                report += f"{month}: {count} відправлень\n"
            
            cur.close()
            
            # Показать отчет в новом окне
            self._show_text_dialog("Звіт по відправленням", report)
            
        except Error as e:
            messagebox.showerror("Помилка", f"Помилка генерації звіту: {e}")

    def _show_text_dialog(self, title, text):
        """Показ текстового диалога"""
        win = tb.Toplevel(self)
        win.title(title)
        win.geometry("500x400")
        
        text_widget = tb.Text(win, wrap="word", padx=10, pady=10)
        text_widget.pack(fill="both", expand=True, padx=10, pady=10)
        text_widget.insert("1.0", text)
        text_widget.config(state="disabled")
        
        tb.Button(win, text="Закрити", command=win.destroy).pack(pady=10)

    def _logout(self):
        """Выход из системы"""
        self.auth_manager.logout()
        self.current_user = None
        self.conn = None
        self._build_login_ui()