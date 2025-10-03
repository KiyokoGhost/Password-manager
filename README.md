# Password Manager

GUI приложение для управления паролями с использованием Python, Tkinter и MySQL.

##  Возможности

-Шифрование паролей с использованием cryptography.Fernet

-Поиск паролей

-Генератор паролей

-Хранение в MySQL базе данных

-Копирование паролей в буфер обмена

##  Установка

### Предварительные требования

- Python 3.7+
- MySQL Server
- pip (менеджер пакетов Python)

## Шаги установки

1. Клонируйте репозиторий
git clone https://github.com/KiyokoGhost/Password-manager

cd Password-manager

2. Установите зависимости
pip install -r requirements.txt

3. Настройте базу данных MySQL
mysql -u root -p -e "CREATE DATABASE password_manager;"

4. Настройте конфигурацию
copy config\config.example.py config\config.py
Отредактируйте config.py своими данными

5. Запустите приложение
python run.pyr
   
## Альтернативные способы запуска
# Через командную строку:

python src\main.py

# Через ярлык (двойной клик):

Просто дважды щелкните по launcher.bat 🖱️

# Настройка конфигурации

Отредактируйте config/config.py:

DB_CONFIG = {
    'host': 'localhost',
    'user': 'ваш_пользователь',      #  Ваш пользователь MySQL
    'password': 'ваш_пароль',        #  Ваш пароль MySQL
    'database': 'password_manager',  #  Название базы данных
    'charset': 'utf8mb4',            #  Кодировка по умолчанию 
    'cursorclass': 'pymysql.cursors.DictCursor'
}