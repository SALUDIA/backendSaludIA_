import os
from dotenv import load_dotenv

def get_db_config():
    """Obtener configuración de base de datos desde variables de entorno"""
    
    # En Render, las variables ya están disponibles
    # No necesitas cargar .env en producción
    if os.getenv('FLASK_ENV') != 'production':
        load_dotenv()
    
    return {
        'host': os.getenv('DB_HOST'),
        'user': os.getenv('DB_USER'), 
        'password': os.getenv('DB_PASSWORD'),
        'database': os.getenv('DB_NAME'),
        'port': int(os.getenv('DB_PORT', 3306)),
        'ssl_required': os.getenv('DB_SSL_REQUIRED', 'false').lower() == 'true',
        'ssl_mode': os.getenv('DB_SSL_MODE', 'disabled')
    }

def get_cors_config():
    """Configuración CORS para producción"""
    origins = os.getenv('CORS_ORIGINS', '*')
    
    if origins == '*':
        origins_list = ['*']
    else:
        origins_list = [origin.strip() for origin in origins.split(',')]
    
    return {
        'origins': origins_list,
        'methods': ['GET', 'POST', 'OPTIONS'],
        'allow_headers': ['Content-Type', 'Authorization', 'X-Requested-With'],
        'supports_credentials': False
    }