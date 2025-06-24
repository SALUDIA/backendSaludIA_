"""
Configuración base compartida
"""
import os
from dotenv import load_dotenv

load_dotenv()

class BaseConfig:
    """Configuración base para todos los entornos"""
    
    # Flask básico
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key')
    FLASK_APP = 'app.py'
    
    # Base de datos por defecto (local)
    @property
    def DB_CONFIG(self):
        return {
            'host': os.getenv('LOCAL_DB_HOST', 'localhost'),
            'database': os.getenv('LOCAL_DB_NAME', 'saludiadb'),
            'user': os.getenv('LOCAL_DB_USER', 'root'),
            'password': os.getenv('LOCAL_DB_PASSWORD', ''),
            'port': int(os.getenv('LOCAL_DB_PORT', 3306)),
            'charset': 'utf8mb4',
            'use_unicode': True,
            'autocommit': True
        }
    
    # Modelo ML
    MODEL_VERSION = 'v8'
    MODEL_PATH = 'models/'
    
    # API
    API_RATE_LIMIT = '100 per hour'
    API_TIMEOUT = 30
    
    # CORS
    @property
    def CORS_ORIGINS(self):
        return ['*']
    
    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Traductor
    TRANSLATOR_SERVICE = 'google'
    TRANSLATOR_TIMEOUT = 10