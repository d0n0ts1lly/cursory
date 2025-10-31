import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox

class LoginView:
    """Представление для экрана входа"""
    
    def __init__(self, parent, auth_manager, on_login_success):
        self.parent = parent
        self.auth_manager = auth_manager
        self.on_login_success = on_login_success
        
        self.entry_username = None
        self.entry_password = None
        
        self._build_ui()
    
    def _build_ui(self):
        """Построение UI входа"""
        for w in self.parent.winfo_children():
            w.destroy()

        # Main container with gradient background
        main_container = tb.Frame(self.parent)
        main_container.pack(fill="both", expand=True)

        # Left side - branding
        left_side = tb.Frame(main_container, bootstyle="light")
        left_side.pack(side="left", fill="both", expand=True, padx=20, pady=40)
        
        tb.Label(left_side, text="🚗", font=("Segoe UI", 72), bootstyle="inverse-light").pack(pady=20)
        tb.Label(left_side, text="Auto Tracker Pro", font=("Segoe UI", 28, "bold"), 
                bootstyle="inverse-light").pack(pady=10)
        tb.Label(left_side, text="Система відстеження транспортних засобів", 
                font=("Segoe UI", 14), bootstyle="inverse-light").pack(pady=5)
        
        features = [
            "✓ Відстеження в реальному часі",
            "✓ Фото-галерея авто",
            "✓ Інтерактивні карти",
            "✓ Сповіщення та сповіщення",
            "✓ Аналітика та звіти"
        ]
        for feature in features:
            tb.Label(left_side, text=feature, font=("Segoe UI", 12), 
                    bootstyle="inverse-light").pack(anchor="w", pady=2)

        # Right side - login form
        right_side = tb.Frame(main_container)
        right_side.pack(side="right", fill="both", expand=True, padx=40, pady=80)

        form_frame = tb.Frame(right_side)
        form_frame.pack(expand=True)

        tb.Label(form_frame, text="Вхід до системи", font=("Segoe UI", 24, "bold")).pack(pady=20)

        # Username field
        tb.Label(form_frame, text="Логін", font=("Segoe UI", 11)).pack(anchor="w", pady=(10,2))
        self.entry_username = tb.Entry(form_frame, width=30, font=("Segoe UI", 11))
        self.entry_username.pack(fill="x", pady=5)
        self.entry_username.bind("<Return>", lambda e: self._do_login())

        # Password field
        tb.Label(form_frame, text="Пароль", font=("Segoe UI", 11)).pack(anchor="w", pady=(10,2))
        self.entry_password = tb.Entry(form_frame, width=30, show="•", font=("Segoe UI", 11))
        self.entry_password.pack(fill="x", pady=5)
        self.entry_password.bind("<Return>", lambda e: self._do_login())

        # Login button
        login_btn = tb.Button(form_frame, text="Увійти", bootstyle="success", 
                             width=20, command=self._do_login)
        login_btn.pack(pady=20)

        # Additional options
        options_frame = tb.Frame(form_frame)
        options_frame.pack(fill="x", pady=10)
        
        tb.Button(options_frame, text="Демо-вхід", bootstyle="outline-secondary",
                 command=self._demo_login).pack(side="left")
        tb.Button(options_frame, text="Забули пароль?", bootstyle="link",
                 command=self._forgot_password).pack(side="right")
    
    def _do_login(self):
        """Выполняет вход"""
        username = self.entry_username.get().strip()
        pwd = self.entry_password.get().strip()
        
        user = self.auth_manager.login(username, pwd)
        if user:
            self.on_login_success(user, self.auth_manager.connection)
    
    def _demo_login(self):
        """Демо-вход для тестирования"""
        demo_creds = self.auth_manager.demo_login()
        self.entry_username.delete(0, 'end')
        self.entry_password.delete(0, 'end')
        self.entry_username.insert(0, demo_creds["username"])
        self.entry_password.insert(0, demo_creds["password"])
        messagebox.showinfo("Демо-вхід", 
                          "Використовуються демо-credentials\nЛогін: demo_user\nПароль: demo123")
    
    def _forgot_password(self):
        """Обработка забытого пароля"""
        messagebox.showinfo("Відновлення пароля", 
                          "Зв'яжіться з адміністратором для відновлення пароля.")