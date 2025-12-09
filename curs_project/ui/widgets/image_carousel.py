import os
import io
import datetime
import urllib.request
import ssl
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import ttkbootstrap as tb
from ttkbootstrap.constants import *
import mysql.connector
from mysql.connector import Error
from config import ASSETS_DIR

class ImageCarousel(tb.Frame):
    def __init__(self, parent, purchase_id, conn, current_user=None):
        super().__init__(parent)
        self.purchase_id = purchase_id
        self.conn = conn
        self.images = []
        self.current_index = 0
        self.image_labels = []
        self.current_user = current_user
        self.can_edit = current_user and current_user.get('role') == 'admin'
        
        self._create_widgets()
        self._load_images()
    
    def _create_widgets(self):
        tb.Label(self, text="🖼️ Галерея фото авто", 
                font=("Segoe UI", 12, "bold")).pack(pady=5)
        
        if self.can_edit:
            btn_frame = tb.Frame(self)
            btn_frame.pack(fill="x", pady=5)
            tb.Button(btn_frame, text="➕ Додати фото", bootstyle="success",
                     command=self._add_image).pack(side="right", padx=5)
        
        self.carousel_frame = tb.Frame(self)
        self.carousel_frame.pack(fill="both", expand=True, pady=5)
        
        nav_frame = tb.Frame(self)
        nav_frame.pack(fill="x", pady=5)
        
        tb.Button(nav_frame, text="◀ Попередня", bootstyle="secondary",
                 command=self._prev_image).pack(side="left", padx=5)
        
        self.status_label = tb.Label(nav_frame, text="", font=("Segoe UI", 9))
        self.status_label.pack(side="left", expand=True)
        
        tb.Button(nav_frame, text="Наступна ▶", bootstyle="secondary",
                 command=self._next_image).pack(side="right", padx=5)
    
    def _load_images(self):
        try:
            cur = self.conn.cursor(dictionary=True)
            cur.execute("""
                SELECT * FROM purchase_images 
                WHERE purchase_id = %s 
                ORDER BY image_type, uploaded_at
            """, (self.purchase_id,))
            self.all_images = cur.fetchall()
            cur.close()
            
            self.images = self.all_images
            self.current_index = 0
            self._display_current_image()
            
        except Error as e:
            print(f"Помилка завантаження фото: {e}")
    
    def _display_current_image(self):
        for widget in self.carousel_frame.winfo_children():
            widget.destroy()
        
        if not self.images:
            no_images_frame = tb.Frame(self.carousel_frame)
            no_images_frame.pack(expand=True)
            
            tb.Label(no_images_frame, text="📷 Немає фото для цього авто",
                    font=("Segoe UI", 10), bootstyle="secondary").pack(pady=20)
            
            if self.can_edit:
                tb.Button(no_images_frame, text="➕ Додати перше фото", bootstyle="success",
                        command=self._add_image).pack(pady=10)
            
            self.status_label.config(text="0 / 0")
            return
        
        current_img = self.images[self.current_index]
        
        img_container = tb.Frame(self.carousel_frame)
        img_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        try:
            image_url = current_img['image_url']
            pil_image = None
            
            if os.path.exists(image_url):
                pil_image = Image.open(image_url)
            elif image_url.startswith(('http://', 'https://')):
                try:
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                    req = urllib.request.Request(image_url, headers=headers)
                    ssl_context = ssl._create_unverified_context()
                    response = urllib.request.urlopen(req, timeout=10, context=ssl_context)
                    image_data = response.read()
                    pil_image = Image.open(io.BytesIO(image_data))
                except Exception as url_error:
                    print(f"Помилка завантаження URL фото: {url_error}")
                    pil_image = self._create_placeholder_image(current_img['image_type'])
            else:
                possible_paths = [
                    image_url,
                    os.path.join(ASSETS_DIR, image_url),
                    os.path.join(os.path.dirname(__file__), image_url),
                    os.path.join(os.path.dirname(__file__), "assets", image_url)
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        pil_image = Image.open(path)
                        break
                
                if not pil_image:
                    pil_image = self._create_placeholder_image(current_img['image_type'])
            
            pil_image.thumbnail((500, 300), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(pil_image)
            
            img_label = tb.Label(img_container, image=photo)
            img_label.image = photo
            img_label.pack(pady=5)
            
            info_frame = tb.Frame(img_container)
            info_frame.pack(fill="x", pady=5)
            
            type_names = {
                'auction': '🏛️ Аукціон',
                'port': '⚓ Порт', 
                'klaipeda': '🚢 Клайпеда'
            }
            
            type_name = type_names.get(current_img['image_type'], current_img['image_type'])
            tb.Label(info_frame, text=f"Тип: {type_name}", 
                    font=("Segoe UI", 9, "bold")).pack()
            
            if current_img.get('notes'):
                tb.Label(info_frame, text=f"Примітки: {current_img['notes']}",
                        font=("Segoe UI", 8), wraplength=400).pack()
        
            if self.can_edit:
                btn_frame = tb.Frame(info_frame)
                btn_frame.pack(pady=5)
                
                tb.Button(btn_frame, text="✏️ Редагувати", bootstyle="warning",
                        command=lambda: self._edit_image(current_img)).pack(side="left", padx=2)
                tb.Button(btn_frame, text="🗑️ Видалити", bootstyle="danger",
                        command=lambda: self._delete_image(current_img)).pack(side="left", padx=2)
            
            self.status_label.config(text=f"{self.current_index + 1} / {len(self.images)}")
            
        except Exception as e:
            print(f"Помилка відображення фото: {e}")
            error_frame = tb.Frame(img_container)
            error_frame.pack(expand=True)
            
            tb.Label(error_frame, text="❌ Помилка завантаження фото",
                    font=("Segoe UI", 10), bootstyle="danger").pack(pady=10)
            
            placeholder = self._create_placeholder_image(current_img['image_type'])
            placeholder.thumbnail((500, 300), Image.Resampling.LANCZOS)
            placeholder_photo = ImageTk.PhotoImage(placeholder)
            
            placeholder_label = tb.Label(error_frame, image=placeholder_photo)
            placeholder_label.image = placeholder_photo
            placeholder_label.pack(pady=10)
            
            tb.Label(error_frame, text="Файл пошкоджено або недоступний",
                    font=("Segoe UI", 9), bootstyle="secondary").pack()
    
    def _create_placeholder_image(self, image_type):
        img = Image.new('RGB', (500, 300), color='#f8f9fa')
        draw = ImageDraw.Draw(img)
        
        icons = {
            'auction': '🏛️',
            'port': '⚓',
            'klaipeda': '🚢'
        }
        
        icon = icons.get(image_type, '📷')
        
        try:
            from PIL import ImageFont
            try:
                font = ImageFont.truetype("arial.ttf", 80)
            except:
                font = ImageFont.load_default()
            
            bbox = draw.textbbox((0, 0), icon, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            x = (500 - text_width) // 2
            y = (300 - text_height) // 2 - 20
            
            draw.text((x, y), icon, fill='#6c757d', font=font)
        except:
            draw.text((200, 120), icon, fill='#6c757d')
        
        type_names = {
            'auction': 'Аукціон',
            'port': 'Порт',
            'klaipeda': 'Клайпеда'
        }
        
        type_text = type_names.get(image_type, image_type)
        draw.text((250, 220), type_text, fill='#495057', anchor="mm")
        
        return img
    
    def _prev_image(self):
        if len(self.images) > 1:
            self.current_index = (self.current_index - 1) % len(self.images)
            self._display_current_image()
    
    def _next_image(self):
        if len(self.images) > 1:
            self.current_index = (self.current_index + 1) % len(self.images)
            self._display_current_image()
    
    def _add_image(self):
        if not self.can_edit:
            messagebox.showwarning("Доступ заборонено", "Тільки адміністратор може додавати фото")
            return
            
        add_dialog = tb.Toplevel(self)
        add_dialog.title("Додати фото")
        add_dialog.geometry("500x450")
        add_dialog.transient(self)
        add_dialog.grab_set()
        
        add_dialog.update_idletasks()
        parent_x = self.winfo_rootx()
        parent_y = self.winfo_rooty()
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()
        
        x = parent_x + (parent_width - 500) // 2
        y = parent_y + (parent_height - 450) // 2
        add_dialog.geometry(f"+{x}+{y}")
        
        tb.Label(add_dialog, text="Додати нове фото", 
                font=("Segoe UI", 14, "bold")).pack(pady=15)
        
        form_frame = tb.Frame(add_dialog)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        tb.Label(form_frame, text="Тип фото:", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=5)
        type_var = tb.StringVar(value="auction")
        type_combo = tb.Combobox(form_frame, textvariable=type_var,
                               values=["auction", "port", "klaipeda"],
                               state="readonly")
        type_combo.pack(fill="x", pady=5)
        
        tb.Label(form_frame, text="Джерело фото:", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=5)
        source_var = tb.StringVar(value="file")
        source_frame = tb.Frame(form_frame)
        source_frame.pack(fill="x", pady=5)
        
        tb.Radiobutton(source_frame, text="З файлу", variable=source_var, value="file",
                      command=lambda: self._toggle_source_fields(form_frame, "file")).pack(side="left", padx=10)
        tb.Radiobutton(source_frame, text="З посилання", variable=source_var, value="url",
                      command=lambda: self._toggle_source_fields(form_frame, "url")).pack(side="left", padx=10)
        
        self.source_container = tb.Frame(form_frame)
        self.source_container.pack(fill="x", pady=5)
        
        self.file_frame = tb.Frame(self.source_container)
        tb.Label(self.file_frame, text="Файл зображення:", font=("Segoe UI", 9)).pack(anchor="w", pady=5)
        file_inner_frame = tb.Frame(self.file_frame)
        file_inner_frame.pack(fill="x", pady=5)
        
        self.file_var = tb.StringVar()
        file_entry = tb.Entry(file_inner_frame, textvariable=self.file_var)
        file_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        def browse_file():
            filename = filedialog.askopenfilename(
                title="Виберіть зображення",
                filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif *.bmp")]
            )
            if filename:
                self.file_var.set(filename)
        
        tb.Button(file_inner_frame, text="📁", bootstyle="outline",
                 command=browse_file).pack(side="right")
        
        self.url_frame = tb.Frame(self.source_container)
        tb.Label(self.url_frame, text="URL зображення:", font=("Segoe UI", 9)).pack(anchor="w", pady=5)
        
        self.url_var = tb.StringVar()
        url_entry = tb.Entry(self.url_frame, textvariable=self.url_var)
        url_entry.pack(fill="x", pady=5)
        url_entry.insert(0, "https://example.com/image.jpg")
        
        self.file_frame.pack(fill="x")
        
        tb.Label(form_frame, text="Примітки:", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=5)
        notes_text = tb.Text(form_frame, height=3, font=("Segoe UI", 9))
        notes_text.pack(fill="x", pady=5)
        
        btn_frame = tb.Frame(form_frame)
        btn_frame.pack(fill="x", pady=15)
        
        def save_image():
            try:
                source = source_var.get()
                image_type = type_var.get()
                notes = notes_text.get("1.0", "end-1c").strip()
                
                if source == "file":
                    file_path = self.file_var.get().strip()
                    if not file_path:
                        messagebox.showerror("Помилка", "Виберіть файл зображення")
                        return
                    
                    if not os.path.exists(file_path):
                        messagebox.showerror("Помилка", "Файл не знайдено")
                        return
                    
                    filename = os.path.basename(file_path)
                    assets_filename = f"{self.purchase_id}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{filename}"
                    assets_path = os.path.join(ASSETS_DIR, assets_filename)
                    
                    import shutil
                    shutil.copy2(file_path, assets_path)
                    image_path = assets_path
                    
                else:
                    url = self.url_var.get().strip()
                    if not url:
                        messagebox.showerror("Помилка", "Введіть URL зображення")
                        return
                    
                    if not url.startswith(('http://', 'https://')):
                        messagebox.showerror("Помилка", "Невірний URL. Повинен починатися з http:// або https://")
                        return
                    
                    image_path = url
                
                cur = self.conn.cursor()
                cur.execute("""
                    INSERT INTO purchase_images (purchase_id, image_url, image_type, notes)
                    VALUES (%s, %s, %s, %s)
                """, (self.purchase_id, image_path, image_type, notes))
                
                self.conn.commit()
                cur.close()
                
                messagebox.showinfo("Успіх", "Фото успішно додано!")
                add_dialog.destroy()
                self._load_images()
                
            except Exception as e:
                messagebox.showerror("Помилка", f"Помилка додавання фото: {str(e)}")
        
        tb.Button(btn_frame, text="💾 Зберегти", bootstyle="success",
                 command=save_image).pack(side="left", padx=5)
        tb.Button(btn_frame, text="❌ Скасувати", bootstyle="secondary",
                 command=add_dialog.destroy).pack(side="right", padx=5)
    
    def _toggle_source_fields(self, parent, source_type):
        for widget in self.source_container.winfo_children():
            widget.pack_forget()
        
        if source_type == "file":
            self.file_frame.pack(fill="x")
        else:
            self.url_frame.pack(fill="x")
    
    def _edit_image(self, image_data):
        if not self.can_edit:
            messagebox.showwarning("Доступ заборонено", "Тільки адміністратор може редагувати фото")
            return
            
        edit_dialog = tb.Toplevel(self)
        edit_dialog.title("Редагувати фото")
        edit_dialog.geometry("500x350")
        edit_dialog.transient(self)
        edit_dialog.grab_set()
        
        edit_dialog.update_idletasks()
        parent_x = self.winfo_rootx()
        parent_y = self.winfo_rooty()
        parent_width = self.winfo_width()
        parent_height = self.winfo_height()
        
        x = parent_x + (parent_width - 500) // 2
        y = parent_y + (parent_height - 350) // 2
        edit_dialog.geometry(f"+{x}+{y}")
        
        tb.Label(edit_dialog, text="Редагувати фото", 
                font=("Segoe UI", 14, "bold")).pack(pady=15)
        
        form_frame = tb.Frame(edit_dialog)
        form_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        tb.Label(form_frame, text="Тип фото:", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=5)
        type_var = tb.StringVar(value=image_data['image_type'])
        type_combo = tb.Combobox(form_frame, textvariable=type_var,
                               values=["auction", "port", "klaipeda"],
                               state="readonly")
        type_combo.pack(fill="x", pady=5)
        
        tb.Label(form_frame, text="Примітки:", font=("Segoe UI", 9, "bold")).pack(anchor="w", pady=5)
        notes_text = tb.Text(form_frame, height=3, font=("Segoe UI", 9))
        notes_text.pack(fill="x", pady=5)
        notes_text.insert("1.0", image_data.get('notes', ''))
        
        btn_frame = tb.Frame(form_frame)
        btn_frame.pack(fill="x", pady=15)
        
        def save_changes():
            try:
                cur = self.conn.cursor()
                cur.execute("""
                    UPDATE purchase_images 
                    SET image_type = %s, notes = %s
                    WHERE image_id = %s
                """, (type_var.get(), notes_text.get("1.0", "end-1c").strip(), image_data['image_id']))
                
                self.conn.commit()
                cur.close()
                
                messagebox.showinfo("Успіх", "Фото успішно оновлено!")
                edit_dialog.destroy()
                self._load_images()
                
            except Exception as e:
                messagebox.showerror("Помилка", f"Помилка оновлення фото: {str(e)}")
        
        tb.Button(btn_frame, text="💾 Зберегти", bootstyle="success",
                 command=save_changes).pack(side="left", padx=5)
        tb.Button(btn_frame, text="🗑️ Видалити", bootstyle="danger",
                 command=lambda: [edit_dialog.destroy(), self._delete_image(image_data)]).pack(side="left", padx=5)
        tb.Button(btn_frame, text="❌ Скасувати", bootstyle="secondary",
                 command=edit_dialog.destroy).pack(side="right", padx=5)
    
    def _delete_image(self, image_data):
        if not self.can_edit:
            messagebox.showwarning("Доступ заборонено", "Тільки адміністратор може видаляти фото")
            return
            
        if not messagebox.askyesno("Підтвердження", "Видалити це фото?"):
            return
        
        try:
            image_url = image_data['image_url']
            is_local_file = False
            
            possible_paths = [
                image_url,
                os.path.join(ASSETS_DIR, image_url),
                os.path.join(os.path.dirname(__file__), image_url),
                os.path.join(os.path.dirname(__file__), "assets", image_url)
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    os.remove(path)
                    is_local_file = True
                    print(f"🗑️ Видалено локальний файл: {path}")
                    break
            
            if not is_local_file and not image_url.startswith(('http://', 'https://')):
                print(f"⚠️ Файл не знайдено локально і не є URL: {image_url}")
            
            cur = self.conn.cursor()
            cur.execute("DELETE FROM purchase_images WHERE image_id = %s", (image_data['image_id'],))
            self.conn.commit()
            cur.close()
            
            messagebox.showinfo("Успіх", "Фото успішно видалено!")
            self._load_images()
            
        except Exception as e:
            messagebox.showerror("Помилка", f"Помилка видалення фото: {str(e)}")
            print(f"❌ Помилка видалення: {e}")