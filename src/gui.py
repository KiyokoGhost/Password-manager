import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import logging
from datetime import datetime
import random
import string

from src.database import DatabaseManager
from src.security import EncryptionManager

logger = logging.getLogger(__name__)

class PasswordManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Менеджер паролей")
        self.root.geometry("900x700")
        
        # Инициализация менеджеров
        self.encryption = EncryptionManager()
        self.db = DatabaseManager()
        if not self.db.connection:
            messagebox.showerror("Ошибка", "Не удалось подключиться к базе данных")
            return
        
        if not self.db.create_table():
            messagebox.showerror("Ошибка", "Не удалось создать таблицу")
            return
        
        self.setup_ui()
        logger.info("Приложение запущено")
    
    def setup_ui(self):
        """Настраивает пользовательский интерфейс"""
        # Статус бар
        self.status_var = tk.StringVar()
        self.status_var.set("Готов к работе")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief='sunken')
        status_bar.pack(side='bottom', fill='x')
        
        # Создаем вкладки
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладки
        self.create_add_tab()
        self.create_view_tab()
        self.create_search_tab()
    
    def create_add_tab(self):
        """Создает вкладку добавления пароля"""
        self.add_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.add_frame, text="Добавить пароль")
        
        # Основные поля
        fields_frame = ttk.Frame(self.add_frame)
        fields_frame.pack(fill='x', padx=10, pady=10)
        
        # Сервис
        ttk.Label(fields_frame, text="Сервис/Сайт:*").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.service_entry = ttk.Entry(fields_frame, width=40)
        self.service_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Имя пользователя
        ttk.Label(fields_frame, text="Имя пользователя:*").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.username_entry = ttk.Entry(fields_frame, width=40)
        self.username_entry.grid(row=1, column=1, padx=5, pady=5)
        
        # Пароль
        ttk.Label(fields_frame, text="Пароль:*").grid(row=2, column=0, padx=5, pady=5, sticky='w')
        self.password_entry = ttk.Entry(fields_frame, width=40, show="*")
        self.password_entry.grid(row=2, column=1, padx=5, pady=5)
        
        # Кнопки для пароля
        password_buttons = ttk.Frame(fields_frame)
        password_buttons.grid(row=2, column=2, columnspan=2, pady=5, sticky='w')
        
        ttk.Button(password_buttons, text="Показать", 
                  command=self.toggle_password_visibility).pack(side='left', padx=2)
        ttk.Button(password_buttons, text="Сгенерировать", 
                  command=self.generate_password).pack(side='left', padx=2)
        
        # Кнопки действий
        button_frame = ttk.Frame(self.add_frame)
        button_frame.pack(pady=15)
        
        ttk.Button(button_frame, text="Сохранить пароль", 
                  command=self.add_password_gui).pack(side='left', padx=5)
        ttk.Button(button_frame, text="Очистить форму", 
                  command=self.clear_form).pack(side='left', padx=5)
        
        # Поле для вывода результата
        self.add_result_text = scrolledtext.ScrolledText(self.add_frame, height=10, width=80)
        self.add_result_text.pack(padx=10, pady=10, fill='both', expand=True)
    
    def create_view_tab(self):
        """Создает вкладку просмотра паролей"""
        self.view_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.view_frame, text="Просмотр паролей")
        
        # Панель инструментов
        toolbar = ttk.Frame(self.view_frame)
        toolbar.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(toolbar, text="Обновить", command=self.view_all_passwords).pack(side='left', padx=2)
        ttk.Button(toolbar, text="Копировать пароль", command=self.copy_password).pack(side='left', padx=2)
        ttk.Button(toolbar, text="Удалить", command=self.delete_selected).pack(side='left', padx=2)
        
        # Поле для вывода
        self.view_result_text = scrolledtext.ScrolledText(self.view_frame, height=20, width=80)
        self.view_result_text.pack(padx=10, pady=10, fill='both', expand=True)
        
        # Загружаем данные
        self.view_all_passwords()
    
    def create_search_tab(self):
        """Создает вкладку поиска"""
        self.search_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.search_frame, text="Поиск пароля")
        
        # Панель поиска
        search_frame = ttk.Frame(self.search_frame)
        search_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(search_frame, text="Поиск по сервису:").grid(row=0, column=0, padx=5, pady=5)
        self.search_entry = ttk.Entry(search_frame, width=40)
        self.search_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Button(search_frame, text="Искать", command=self.search_passwords).grid(row=0, column=2, padx=5)
        ttk.Button(search_frame, text="Сбросить", command=self.reset_search).grid(row=0, column=3, padx=5)
        
        # Результаты поиска
        self.search_result_text = scrolledtext.ScrolledText(self.search_frame, height=20, width=80)
        self.search_result_text.pack(padx=10, pady=10, fill='both', expand=True)

    def toggle_password_visibility(self):
        """Переключает видимость пароля"""
        if self.password_entry.cget('show') == '*':
            self.password_entry.config(show='')
        else:
            self.password_entry.config(show='*')

    def generate_password(self):
        """Генерирует случайный пароль"""
        length = 12
        characters = string.ascii_letters + string.digits + "!@#$%^&*"
        password = ''.join(random.choice(characters) for i in range(length))
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, password)

    def add_password_gui(self):
        """Добавляет пароль через графический интерфейс"""
        service = self.service_entry.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        
        if not service or not username or not password:
            messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
            return
        
        try:
            # Шифруем пароль перед сохранением
            encrypted_password = self.encryption.encrypt_password(password)
            action = self.db.add_or_update_password(service, username, encrypted_password)
            
            result_text = f"Пароль успешно {action}!\n\n"
            result_text += f"Сервис: {service}\n"
            result_text += f"Пользователь: {username}\n"
            result_text += f"Пароль: {password}\n"
            result_text += f"Время: {self.get_current_time()}\n"
            
            self.add_result_text.delete(1.0, tk.END)
            self.add_result_text.insert(1.0, result_text)
            
            # Очищаем поля ввода
            self.service_entry.delete(0, tk.END)
            self.username_entry.delete(0, tk.END)
            self.password_entry.delete(0, tk.END)
            
            # Обновляем список паролей
            self.view_all_passwords()
            self.update_status(f"Пароль для {service} {action}")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при сохранении пароля: {e}")
            logger.error(f"Ошибка при добавлении пароля: {e}")

    def view_all_passwords(self):
        """Показывает все сохраненные пароли"""
        try:
            results = self.db.get_all_passwords()
            
            result_text = "ВСЕ СОХРАНЕННЫЕ ПАРОЛИ:\n"
            result_text += "=" * 60 + "\n\n"
            
            if results:
                for i, row in enumerate(results, 1):
                    try:
                        # Расшифровываем пароль для отображения
                        decrypted_password = self.encryption.decrypt_password(row['password_text'])
                        
                        result_text += f"{i}. СЕРВИС: {row['service']}\n"
                        result_text += f"   Пользователь: {row['username']}\n"
                        result_text += f"   Пароль: {decrypted_password}\n"
                        result_text += f"   Добавлен: {row['created_at']}\n"
                        result_text += "-" * 40 + "\n"
                    except Exception as decrypt_error:
                        # Если не удалось расшифровать, показываем ошибку
                        result_text += f"{i}. СЕРВИС: {row['service']}\n"
                        result_text += f"   Пользователь: {row['username']}\n"
                        result_text += f"   ОШИБКА ДЕШИФРОВАНИЯ: {decrypt_error}\n"
                        result_text += f"   Добавлен: {row['created_at']}\n"
                        result_text += "-" * 40 + "\n"
                
                result_text += f"\nВсего сохранено записей: {len(results)}"
            else:
                result_text += "Нет сохраненных паролей.\n"
                result_text += "Добавьте пароли во вкладке 'Добавить пароль'"
            
            self.view_result_text.delete(1.0, tk.END)
            self.view_result_text.insert(1.0, result_text)
            self.update_status(f"Загружено {len(results)} записей")
            
        except Exception as e:
            error_msg = f"Ошибка при загрузке паролей: {e}"
            messagebox.showerror("Ошибка", error_msg)
            logger.error(f"Ошибка при просмотре паролей: {e}")

    def search_passwords(self):
        """Выполняет поиск паролей"""
        search_term = self.search_entry.get().strip()
        
        if not search_term:
            messagebox.showwarning("Внимание", "Введите поисковый запрос!")
            return
        
        try:
            results = self.db.search_passwords(search_term)
            
            result_text = f"РЕЗУЛЬТАТЫ ПОИСКА ('{search_term}'):\n"
            result_text += "=" * 60 + "\n\n"
            
            if results:
                for i, row in enumerate(results, 1):
                    try:
                        decrypted_password = self.encryption.decrypt_password(row['password_text'])
                        
                        result_text += f"{i}. СЕРВИС: {row['service']}\n"
                        result_text += f"   Пользователь: {row['username']}\n"
                        result_text += f"   Пароль: {decrypted_password}\n"
                        result_text += f"   Добавлен: {row['created_at']}\n"
                        result_text += "-" * 40 + "\n"
                    except Exception as decrypt_error:
                        result_text += f"{i}. СЕРВИС: {row['service']}\n"
                        result_text += f"   Пользователь: {row['username']}\n"
                        result_text += f"   ОШИБКА ДЕШИФРОВАНИЯ: {decrypt_error}\n"
                        result_text += f"   Добавлен: {row['created_at']}\n"
                        result_text += "-" * 40 + "\n"
                
                result_text += f"\nНайдено записей: {len(results)}"
            else:
                result_text += f"По запросу '{search_term}' ничего не найдено.\n"
            
            self.search_result_text.delete(1.0, tk.END)
            self.search_result_text.insert(1.0, result_text)
            self.update_status(f"Найдено {len(results)} записей")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при поиске: {e}")
            logger.error(f"Ошибка при поиске: {e}")

    def copy_password(self):
        """Копирует пароль в буфер обмена"""
        try:
            selected_text = self.view_result_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            if selected_text:
                lines = selected_text.split('\n')
                for line in lines:
                    if line.strip().startswith('Пароль:'):
                        password = line.replace('Пароль:', '').strip()
                        self.root.clipboard_clear()
                        self.root.clipboard_append(password)
                        self.update_status("Пароль скопирован в буфер обмена")
                        messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена")
                        return
                
                messagebox.showwarning("Внимание", "Не удалось найти пароль в выделенном тексте")
            else:
                messagebox.showwarning("Внимание", "Выделите текст с паролем")
                
        except tk.TclError:
            messagebox.showwarning("Внимание", "Выделите текст с паролем")

    def delete_selected(self):
        """Удаляет выбранный пароль"""
        try:
            selected_text = self.view_result_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            if selected_text:
                lines = selected_text.split('\n')
                service = None
                username = None
                
                for line in lines:
                    if line.strip().startswith('СЕРВИС:'):
                        service = line.replace('СЕРВИС:', '').strip()
                    elif line.strip().startswith('Пользователь:'):
                        username = line.replace('Пользователь:', '').strip()
                
                if service and username:
                    if messagebox.askyesno("Подтверждение", f"Удалить пароль для {service} ({username})?"):
                        try:
                            self.db.delete_password(service, username)
                            messagebox.showinfo("Успех", "Пароль удален")
                            self.view_all_passwords()
                            self.update_status(f"Удален пароль для {service}")
                            
                        except Exception as e:
                            messagebox.showerror("Ошибка", f"Ошибка при удалении: {e}")
                else:
                    messagebox.showwarning("Внимание", "Не удалось определить запись для удаления")
            else:
                messagebox.showwarning("Внимание", "Выделите запись для удаления")
                
        except tk.TclError:
            messagebox.showwarning("Внимание", "Выделите запись для удаления")

    def clear_form(self):
        """Очищает форму добавления пароля"""
        self.service_entry.delete(0, tk.END)
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.add_result_text.delete(1.0, tk.END)
        self.update_status("Форма очищена")

    def reset_search(self):
        """Сбрасывает поиск"""
        self.search_entry.delete(0, tk.END)
        self.search_result_text.delete(1.0, tk.END)
        self.update_status("Поиск сброшен")

    def update_status(self, message):
        """Обновляет статус бар"""
        self.status_var.set(f"{self.get_current_time()} | {message}")

    def get_current_time(self):
        """Возвращает текущее время в формате строки"""
        return datetime.now().strftime("%H:%M:%S")

    def __del__(self):
        """Закрывает соединения при удалении объекта"""
        if hasattr(self, 'db'):
            self.db.close()