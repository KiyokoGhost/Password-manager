import pymysql
import logging
from config.config import DB_CONFIG

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """Устанавливает соединение с базой данных"""
        try:
            # Проверяем наличие всех необходимых параметров
            required_fields = ['host', 'user', 'password', 'database']
            for field in required_fields:
                if field not in DB_CONFIG:
                    raise ValueError(f"Отсутствует обязательный параметр: {field}")
            
            # Подключаемся к базе данных
            self.connection = pymysql.connect(
                host=DB_CONFIG['host'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['database'],
                charset=DB_CONFIG.get('charset', 'utf8mb4'),
                cursorclass=pymysql.cursors.DictCursor
            )
            
            logger.info("Подключение к БД установлено")
            print("[SUCCESS] Успешное подключение к базе данных")
            return True
            
        except pymysql.Error as e:
            error_msg = f"Ошибка подключения к базе данных: {e}"
            logger.error(error_msg)
            print(f"[ERROR] {error_msg}")
            print("Проверьте:")
            print(f"  - Хост: {DB_CONFIG.get('host', 'не указан')}")
            print(f"  - Пользователь: {DB_CONFIG.get('user', 'не указан')}")
            print(f"  - База данных: {DB_CONFIG.get('database', 'не указана')}")
            print(f"  - Убедитесь, что MySQL сервер запущен")
            print(f"  - Убедитесь, что база данных '{DB_CONFIG.get('database')}' существует")
            return False
        
        except Exception as e:
            error_msg = f"Неожиданная ошибка при подключении: {e}"
            logger.error(error_msg)
            print(f"[ERROR] {error_msg}")
            return False
    
    def create_table(self):
        """Создает таблицу для хранения паролей"""
        if not self.connection:
            print("[ERROR] Нет подключения к БД для создания таблицы")
            return False
            
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS passwords (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        service VARCHAR(255) NOT NULL,
                        username VARCHAR(255) NOT NULL,
                        password_text VARCHAR(500) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE KEY unique_service_username (service, username)
                    ) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
                """)
                self.connection.commit()
                logger.info("Таблица создана/проверена")
                print("[SUCCESS] Таблица passwords создана/проверена")
                return True
                
        except pymysql.Error as e:
            error_msg = f"Ошибка при создании таблицы: {e}"
            logger.error(error_msg)
            print(f"[ERROR] {error_msg}")
            return False
    
    def add_or_update_password(self, service, username, encrypted_password):
        """Добавляет или обновляет пароль"""
        if not self.connection:
            raise Exception("Нет подключения к базе данных")
            
        try:
            with self.connection.cursor() as cursor:
                # Проверяем существование записи
                check_sql = "SELECT id FROM passwords WHERE service = %s AND username = %s"
                cursor.execute(check_sql, (service, username))
                existing = cursor.fetchone()
                
                if existing:
                    # Обновляем существующую запись
                    update_sql = "UPDATE passwords SET password_text = %s, created_at = CURRENT_TIMESTAMP WHERE service = %s AND username = %s"
                    cursor.execute(update_sql, (encrypted_password, service, username))
                    action = "обновлен"
                else:
                    # Добавляем новую запись
                    insert_sql = "INSERT INTO passwords (service, username, password_text) VALUES (%s, %s, %s)"
                    cursor.execute(insert_sql, (service, username, encrypted_password))
                    action = "добавлен"
                
                self.connection.commit()
                logger.info(f"Пароль для {service} {action}")
                print(f"[SUCCESS] Пароль для {service} успешно {action}")
                return action
                
        except pymysql.Error as e:
            error_msg = f"Ошибка при сохранении пароля: {e}"
            logger.error(error_msg)
            print(f"[ERROR] {error_msg}")
            raise
    
    def get_all_passwords(self):
        """Возвращает все пароли"""
        if not self.connection:
            raise Exception("Нет подключения к базе данных")
            
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT service, username, password_text, created_at 
                    FROM passwords 
                    ORDER BY service, username
                """)
                results = cursor.fetchall()
                print(f"[SUCCESS] Загружено {len(results)} записей из базы данных")
                return results
                
        except pymysql.Error as e:
            error_msg = f"Ошибка при загрузке паролей: {e}"
            logger.error(error_msg)
            print(f"[ERROR] {error_msg}")
            raise
    
    def search_passwords(self, search_term):
        """Ищет пароли по сервису"""
        if not self.connection:
            raise Exception("Нет подключения к базе данных")
            
        try:
            with self.connection.cursor() as cursor:
                sql = """
                    SELECT service, username, password_text, created_at 
                    FROM passwords 
                    WHERE service LIKE %s 
                    ORDER BY service, username
                """
                cursor.execute(sql, (f'%{search_term}%',))
                results = cursor.fetchall()
                print(f"[SUCCESS] Найдено {len(results)} записей по запросу '{search_term}'")
                return results
                
        except pymysql.Error as e:
            error_msg = f"Ошибка при поиске: {e}"
            logger.error(error_msg)
            print(f"[ERROR] {error_msg}")
            raise
    
    def delete_password(self, service, username):
        """Удаляет пароль"""
        if not self.connection:
            raise Exception("Нет подключения к базе данных")
            
        try:
            with self.connection.cursor() as cursor:
                # Сначала проверим существование записи
                check_sql = "SELECT id FROM passwords WHERE service = %s AND username = %s"
                cursor.execute(check_sql, (service, username))
                existing = cursor.fetchone()
                
                if not existing:
                    raise Exception(f"Запись для {service} ({username}) не найдена")
                
                # Удаляем запись
                delete_sql = "DELETE FROM passwords WHERE service = %s AND username = %s"
                cursor.execute(delete_sql, (service, username))
                self.connection.commit()
                
                logger.info(f"Пароль для {service} удален")
                print(f"[SUCCESS] Пароль для {service} ({username}) удален")
                return True
                
        except pymysql.Error as e:
            error_msg = f"Ошибка при удалении: {e}"
            logger.error(error_msg)
            print(f"[ERROR] {error_msg}")
            raise
    
    def test_connection(self):
        """Тестирует соединение с базой данных"""
        try:
            if self.connection and self.connection.open:
                with self.connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    print("[SUCCESS] Соединение с БД активно")
                    return True
            else:
                print("[ERROR] Соединение с БД не активно")
                return False
        except Exception as e:
            print(f"[ERROR] Ошибка тестирования соединения: {e}")
            return False
    
    def close(self):
        """Закрывает соединение с БД"""
        if self.connection:
            try:
                self.connection.close()
                logger.info("Соединение с БД закрыто")
                print("[SUCCESS] Соединение с базой данных закрыто")
            except Exception as e:
                logger.error(f"Ошибка при закрытии соединения: {e}")
                print(f"[ERROR] Ошибка при закрытии соединения: {e}")