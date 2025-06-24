"""
Configuración específica para entorno de producción con Aiven MySQL
"""
import os
from .base import BaseConfig

class ProductionConfig(BaseConfig):
    """Configuración de producción con Aiven MySQL"""
    DEBUG = False
    FLASK_ENV = 'production'
    TESTING = False
    
    @property
    def DB_CONFIG(self):
        """Configuración específica para Aiven MySQL - SOLO VARIABLES DE ENTORNO"""
        return {
            'host': os.getenv('DB_HOST'),  # ← SIN FALLBACK CON CREDENCIALES
            'database': os.getenv('DB_NAME', 'defaultdb'),
            'user': os.getenv('DB_USER'),  # ← SIN FALLBACK CON CREDENCIALES
            'password': os.getenv('DB_PASSWORD'),  # ← SIN FALLBACK CON CREDENCIALES
            'port': int(os.getenv('DB_PORT', 28633)),
            'charset': 'utf8mb4',
            'use_unicode': True,
            'autocommit': True,
            
            # SSL REQUERIDO PARA AIVEN
            'ssl_disabled': False,
            'ssl_verify_cert': False,
            'ssl_verify_identity': False,
            
            # Pool de conexiones optimizado
            'pool_name': 'saludia_aiven_pool',
            'pool_size': 5,
            'pool_reset_session': True,
            'connection_timeout': 20
        }
    
    # Logging optimizado
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
    
    # CORS flexible
    @property
    def CORS_ORIGINS(self):
        origins = os.getenv('CORS_ORIGINS', '*')
        if origins == '*':
            return ['*']
        return origins.split(',')
    
    # Rutas de modelo
    MODEL_PATH = os.getenv('MODEL_PATH', 'models/')
    
    # API con límites
    API_RATE_LIMIT = '60 per minute'
    API_TIMEOUT = 30
    
    # Seguridad SIN FALLBACKS CON CREDENCIALES
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-this-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'change-this-in-production')
    
    @classmethod
    def validate(cls):
        """Validar configuraciones críticas"""
        required_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD']
        missing = [var for var in required_vars if not os.getenv(var)]
        
        if missing:
            print(f"❌ Variables críticas faltantes: {missing}")
            print("💡 Configúralas en variables de entorno")
            return False
        else:
            print("✅ Todas las variables de BD configuradas")
            return True