import os
import sys
import tkinter as tk
import logging

# Настройка кодировки для Windows ДО любых выводов
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass  # Если reconfigure не доступен

# Добавляем корневую директорию проекта в путь Python
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from src.gui import PasswordManagerGUI
    print("[SUCCESS] Все модули импортированы успешно")
except ImportError as e:
    print(f"[ERROR] Ошибка импорта: {e}")
    sys.exit(1)

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('password_manager.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def main():
    """Основная функция приложения"""
    try:
        # Создаем главное окно
        root = tk.Tk()
        
        # Устанавливаем заголовок окна
        root.title("Менеджер паролей")
        
        # Устанавливаем размер окна
        root.geometry("900x700")
        
        # Создаем экземпляр приложения
        app = PasswordManagerGUI(root)
        
        # Запускаем главный цикл приложения
        root.mainloop()
        
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске приложения: {e}")
        print(f"[ERROR] Критическая ошибка: {e}")

if __name__ == "__main__":
    main()