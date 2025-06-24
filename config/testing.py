"""
Configuración específica para entorno de testing
"""
import os
from .base import BaseConfig

class TestingConfig(BaseConfig):
    """Configuración de testing"""
    DEBUG = False
    FLASK_ENV = 'testing'
    TESTING = True
    
    # Base de datos de testing
    @property
    def DB_CONFIG(self):
        return {
            'host': os.getenv('TEST_DB_HOST', 'localhost'),
            'database': os.getenv('TEST_DB_NAME', 'saludiadb_test'),
            'user': os.getenv('TEST_DB_USER', 'root'),
            'password': os.getenv('TEST_DB_PASSWORD', ''),
            'port': int(os.getenv('TEST_DB_PORT', 3306)),
            'charset': 'utf8mb4',
            'use_unicode': True,
            'autocommit': True
        }
    
    # Logging mínimo para tests
    LOG_LEVEL = 'WARNING'
    
    # API sin límites para tests
    API_RATE_LIMIT = '10000 per hour'