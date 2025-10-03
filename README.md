markdown
# Password Manager

Простое и безопасное приложение для управления паролями с графическим интерфейсом.

## 📋 Возможности

- Шифрование паролей (cryptography.Fernet)
- Поиск и фильтрация паролей
- Генератор безопасных паролей
- Хранение в MySQL базе данных
- Копирование паролей в буфер обмена

## 🚀 Установка

### Требования
- Python 3.7+
- MySQL Server
- pip

### Быстрая установка

1. **Клонируйте репозиторий**
   ```bash
   git clone https://github.com/KiyokoGhost/Password-manager
   cd Password-manager
Установите зависимости

bash
pip install -r requirements.txt
Настройте базу данных

bash
mysql -u root -p -e "CREATE DATABASE password_manager;"
Настройте конфигурацию

bash
copy config\config.example.py config\config.py
Отредактируйте config.py своими данными

Запустите приложение

bash
python run.py
🎮 Способы запуска
Командная строка: python src\main.py

Ярлык: Дважды щелкните по launcher.bat

⚙️ Настройка
Файл config/config.py:

python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'ваш_пользователь',
    'password': 'ваш_пароль', 
    'database': 'password_manager',
    'charset': 'utf8mb4',
    'cursorclass': 'pymysql.cursors.DictCursor'
}
