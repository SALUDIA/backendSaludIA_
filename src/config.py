import os
from dotenv import load_dotenv

# Solo cargar .env en desarrollo
if os.getenv('FLASK_ENV') != 'production':
    load_dotenv()

class Config:
    """Configuración para desarrollo y producción"""
    
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')
    DEBUG = os.environ.get('DEBUG_MODE', 'false').lower() == 'true'
    
    # Base de datos - CRÍTICO PARA RENDER
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'saludiadb')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    
    # Environment detection
    IS_PRODUCTION = os.environ.get('FLASK_ENV') == 'production'
    
    # Logging
    @classmethod
    def print_config(cls):
        print(f"🔧 Configuración BD:")
        print(f"   Host: {cls.DB_HOST}")
        print(f"   Usuario: {cls.DB_USER}")
        print(f"   Base: {cls.DB_NAME}")
        print(f"   Puerto: {cls.DB_PORT}")
        print(f"   Entorno: {os.environ.get('FLASK_ENV', 'development')}")
        print(f"   Es producción: {cls.IS_PRODUCTION}")
    
    @classmethod
    def get_db_config(cls):
        """Retorna configuración de BD para Render"""
        config = {
            'host': cls.DB_HOST,
            'user': cls.DB_USER,
            'password': cls.DB_PASSWORD,
            'database': cls.DB_NAME,
            'port': cls.DB_PORT,
            'autocommit': True,
            'connection_timeout': 30
        }
        
        # SSL para Aiven en producción
        if cls.IS_PRODUCTION and 'aiven' in cls.DB_HOST.lower():
            print("🔒 Configurando SSL para Aiven")
            config['ssl_disabled'] = False
        else:
            config['ssl_disabled'] = True
        
        return config