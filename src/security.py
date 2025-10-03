from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
import os
import logging

logger = logging.getLogger(__name__)

class EncryptionManager:
    def __init__(self, key_path='encryption.key'):
        self.key_path = key_path
        self.key = self.load_or_create_key()
        
        # Проверяем валидность ключа перед созданием Fernet
        try:
            self.fernet = Fernet(self.key)
            print("[SUCCESS] Ключ шифрования инициализирован")
        except Exception as e:
            logger.error(f"Неверный ключ шифрования: {e}")
            print(f"[ERROR] Неверный ключ шифрования: {e}")
            print("[INFO] Генерируем новый ключ...")
            # Генерируем новый ключ при ошибке
            self.key = self.generate_new_key()
            self.fernet = Fernet(self.key)
    
    def load_or_create_key(self):
        """Загружает существующий ключ или создает новый"""
        try:
            if os.path.exists(self.key_path):
                # Читаем как бинарный файл
                with open(self.key_path, 'rb') as key_file:
                    key = key_file.read().strip()
                
                print(f"[DEBUG] Прочитано {len(key)} байт из файла ключа")
                
                # Проверяем базовую валидность ключа
                if len(key) != 44:  # Fernet ключ всегда 44 байта в base64
                    raise ValueError(f"Неверная длина ключа: {len(key)} (ожидается 44)")
                
                # Пробуем создать Fernet для проверки ключа
                try:
                    Fernet(key)
                    logger.info("Ключ шифрования загружен и проверен")
                    print("[SUCCESS] Ключ шифрования загружен из файла и проверен")
                    return key
                except Exception as fernet_error:
                    raise ValueError(f"Ключ невалиден для Fernet: {fernet_error}")
            else:
                print("[INFO] Файл ключа не найден, создаем новый")
                return self.generate_new_key()
                
        except Exception as e:
            logger.error(f"Ошибка при загрузке ключа: {e}. Создаем новый.")
            print(f"[ERROR] Ошибка при загрузке ключа: {e}")
            return self.generate_new_key()
    
    def generate_new_key(self):
        """Генерирует новый ключ и сохраняет в файл"""
        key = Fernet.generate_key()
        with open(self.key_path, 'wb') as key_file:
            key_file.write(key)
        logger.info("Новый ключ шифрования создан")
        print("[SUCCESS] Новый ключ шифрования создан и сохранен")
        print(f"[DEBUG] Новый ключ: {key.decode('utf-8')}")
        return key
    
    def encrypt_password(self, password):
        """Шифрует пароль"""
        try:
            if not password:
                raise ValueError("Пароль не может быть пустым")
                
            encrypted = self.fernet.encrypt(password.encode('utf-8'))
            return encrypted.decode('utf-8')
        except Exception as e:
            logger.error(f"Ошибка при шифровании пароля: {e}")
            print(f"[ERROR] Ошибка при шифровании пароля: {e}")
            raise
    
    def decrypt_password(self, encrypted_password):
        """Расшифровывает пароль"""
        try:
            if not encrypted_password:
                raise ValueError("Зашифрованный пароль не может быть пустым")
            
            # Декодируем из строки в байты
            encrypted_bytes = encrypted_password.encode('utf-8')
            
            # Пытаемся расшифровать
            decrypted = self.fernet.decrypt(encrypted_bytes)
            
            # Декодируем результат в строку
            return decrypted.decode('utf-8')
            
        except InvalidToken as e:
            # Специфическая ошибка для неверного ключа или поврежденных данных
            error_msg = f"Неверный токен: возможно, неверный ключ шифрования или поврежденные данные. Ошибка: {e}"
            logger.error(error_msg)
            print(f"[ERROR] {error_msg}")
            
            # Показываем дополнительную диагностику
            print(f"[DEBUG] Длина зашифрованных данных: {len(encrypted_password)}")
            print(f"[DEBUG] Первые 20 символов зашифрованных данных: {encrypted_password[:20]}")
            
            # Создаем информативное сообщение для пользователя
            user_friendly_msg = (
                "Ошибка расшифровки: неверный ключ шифрования.\n\n"
                "Возможные причины:\n"
                "• Файл encryption.key был заменен\n"
                "• Данные в базе были зашифрованы другим ключом\n"
                "• Повреждение данных\n\n"
                "Решение: удалите старые записи и создайте новые с текущим ключом."
            )
            raise Exception(user_friendly_msg) from e
            
        except Exception as e:
            # Общая ошибка дешифрования
            error_msg = f"Ошибка при расшифровке пароля: {e}"
            logger.error(error_msg)
            print(f"[ERROR] {error_msg}")
            
            # Логируем дополнительную информацию для отладки
            if encrypted_password:
                print(f"[DEBUG] Тип зашифрованных данных: {type(encrypted_password)}")
                print(f"[DEBUG] Длина: {len(encrypted_password)}")
            
            raise
    
    def test_encryption(self, test_string="test_password"):
        """Тестирует работу шифрования/дешифрования"""
        try:
            print(f"[TEST] Тестируем шифрование строки: '{test_string}'")
            
            # Шифруем
            encrypted = self.encrypt_password(test_string)
            print(f"[TEST] Успешно зашифровано, длина: {len(encrypted)}")
            
            # Дешифруем
            decrypted = self.decrypt_password(encrypted)
            print(f"[TEST] Успешно дешифровано: '{decrypted}'")
            
            # Проверяем совпадение
            if decrypted == test_string:
                print("[TEST] ✅ Тест шифрования пройден успешно")
                return True
            else:
                print(f"[TEST] ❌ Ошибка: исходная строка '{test_string}' не совпадает с дешифрованной '{decrypted}'")
                return False
                
        except Exception as e:
            print(f"[TEST] ❌ Тест шифрования не пройден: {e}")
            return False
    
    def get_key_info(self):
        """Возвращает информацию о ключе (для отладки)"""
        try:
            key_str = self.key.decode('utf-8') if isinstance(self.key, bytes) else str(self.key)
            return {
                'length': len(self.key),
                'first_10_chars': key_str[:10] + '...',
                'path': self.key_path,
                'exists': os.path.exists(self.key_path)
            }
        except Exception as e:
            return {'error': f"Не удалось получить информацию о ключе: {e}"}


# Дополнительная функция для диагностики
def diagnose_encryption_issue():
    """Функция для диагностики проблем с шифрованием"""
    print("\n" + "="*50)
    print("ДИАГНОСТИКА ШИФРОВАНИЯ")
    print("="*50)
    
    try:
        # Проверяем существование файла ключа
        key_path = 'encryption.key'
        if os.path.exists(key_path):
            file_size = os.path.getsize(key_path)
            print(f"[DIAG] Файл ключа существует: {key_path}")
            print(f"[DIAG] Размер файла: {file_size} байт")
            
            # Читаем ключ
            with open(key_path, 'rb') as f:
                key_content = f.read()
                print(f"[DIAG] Длина ключа: {len(key_content)} байт")
                print(f"[DIAG] Первые 20 байт ключа: {key_content[:20].hex()}")
        else:
            print(f"[DIAG] Файл ключа не найден: {key_path}")
        
        # Создаем менеджер шифрования
        print("\n[DIAG] Создаем EncryptionManager...")
        manager = EncryptionManager()
        
        # Получаем информацию о ключе
        key_info = manager.get_key_info()
        print(f"[DIAG] Информация о ключе: {key_info}")
        
        # Тестируем шифрование
        print("\n[DIAG] Запускаем тест шифрования...")
        test_result = manager.test_encryption()
        
        print(f"\n[DIAG] Результат диагностики: {'✅ УСПЕХ' if test_result else '❌ ОБНАРУЖЕНЫ ПРОБЛЕМЫ'}")
        return test_result
        
    except Exception as e:
        print(f"[DIAG] ❌ Ошибка при диагностике: {e}")
        return False


if __name__ == "__main__":
    # Если файл запущен напрямую, выполняем диагностику
    diagnose_encryption_issue()