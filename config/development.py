"""
Configuración específica para entorno de desarrollo
"""
import os
from .base import BaseConfig

class DevelopmentConfig(BaseConfig):
    """Configuración de desarrollo"""
    DEBUG = True
    FLASK_ENV = 'development'
    TESTING = False
    
    # Base de datos local
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
            'autocommit': True,
            'pool_size': 2,
            'pool_name': 'dev_pool'
        }
    
    # Logging más detallado
    LOG_LEVEL = 'DEBUG'
    
    # CORS permisivo para desarrollo
    @property
    def CORS_ORIGINS(self):
        return ['*']
    
    # API sin límites en desarrollo
    API_RATE_LIMIT = '1000 per hour'