import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración actualizada para usar Aiven"""
    
    # Configuración de base de datos
    FORCE_AIVEN = os.getenv('FORCE_AIVEN', 'false').lower() == 'true'
    
    # Aiven DB (Producción/Testing)
    AIVEN_DB_HOST = os.getenv('DB_HOST')
    AIVEN_DB_USER = os.getenv('DB_USER')
    AIVEN_DB_PASSWORD = os.getenv('DB_PASSWORD')
    AIVEN_DB_NAME = os.getenv('DB_NAME', 'saludia_db')
    AIVEN_DB_PORT = int(os.getenv('DB_PORT', 28633))
    
    # Local DB (Desarrollo)
    LOCAL_DB_HOST = os.getenv('LOCAL_DB_HOST', 'localhost')
    LOCAL_DB_USER = os.getenv('LOCAL_DB_USER', 'root')
    LOCAL_DB_PASSWORD = os.getenv('LOCAL_DB_PASSWORD', '')
    LOCAL_DB_NAME = os.getenv('LOCAL_DB_NAME', 'saludiadb')
    LOCAL_DB_PORT = int(os.getenv('LOCAL_DB_PORT', 3306))
    
    # SSL
    DB_SSL_REQUIRED = os.getenv('DB_SSL_REQUIRED', 'false').lower() == 'true'
    DB_SSL_VERIFY_CERT = os.getenv('DB_SSL_VERIFY_CERT', 'false').lower() == 'true'
    
    # Otras configuraciones
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('DEBUG_MODE', 'false').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
    
    @staticmethod
    def get_db_config():
        """Retorna configuración de BD según FORCE_AIVEN"""
        if Config.FORCE_AIVEN:
            print("🌐 Usando base de datos AIVEN (Producción)")
            return {
                'host': Config.AIVEN_DB_HOST,
                'user': Config.AIVEN_DB_USER,
                'password': Config.AIVEN_DB_PASSWORD,
                'database': Config.AIVEN_DB_NAME,
                'port': Config.AIVEN_DB_PORT,
                'ssl_disabled': not Config.DB_SSL_REQUIRED,
                'autocommit': True
            }
        else:
            print("🏠 Usando base de datos LOCAL (Desarrollo)")
            return {
                'host': Config.LOCAL_DB_HOST,
                'user': Config.LOCAL_DB_USER,
                'password': Config.LOCAL_DB_PASSWORD,
                'database': Config.LOCAL_DB_NAME,
                'port': Config.LOCAL_DB_PORT,
                'ssl_disabled': True,
                'autocommit': True
            }