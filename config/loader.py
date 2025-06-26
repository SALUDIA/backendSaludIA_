import os
from dotenv import load_dotenv

# Cargar .env solo en desarrollo
if os.getenv('FLASK_ENV') != 'production':
    load_dotenv()

def get_db_config():
    """Configuración de base de datos optimizada para Aiven"""
    
    # Determinar si usar Aiven o BD local
    use_aiven = (
        os.getenv('FLASK_ENV') == 'production' or 
        os.getenv('FORCE_AIVEN', 'false').lower() == 'true'
    )
    
    if use_aiven:
        # 🌐 CONFIGURACIÓN AIVEN MYSQL
        return {
            'host': os.getenv('DB_HOST'),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME', 'saludia_db'),
            'port': int(os.getenv('DB_PORT', 28633)),
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci',
            'autocommit': True,
            'raise_on_warnings': True,
            # ✅ SSL configurado correctamente para Aiven
            'ssl_disabled': False,
            'ssl_verify_cert': False,
            'ssl_verify_identity': False,
            'ssl_ca': None,
            'use_unicode': True,
            'connect_timeout': 30,
            'sql_mode': 'TRADITIONAL'
        }
    else:
        # 🏠 CONFIGURACIÓN LOCAL MYSQL
        return {
            'host': os.getenv('LOCAL_DB_HOST', 'localhost'),
            'user': os.getenv('LOCAL_DB_USER', 'root'),
            'password': os.getenv('LOCAL_DB_PASSWORD', ''),
            'database': os.getenv('LOCAL_DB_NAME', 'saludiadb'),
            'port': int(os.getenv('LOCAL_DB_PORT', 3306)),
            'charset': 'utf8mb4',
            'collation': 'utf8mb4_unicode_ci',
            'autocommit': True,
            'ssl_disabled': True,  # ← Sin SSL para local
            'connect_timeout': 10
        }

def get_config_instance():
    """Instancia de configuración"""
    return {
        'database': get_db_config(),
        'debug': os.getenv('FLASK_ENV') == 'development',
        'secret_key': os.getenv('SECRET_KEY', 'dev-key-change-in-production'),
        'cors_origins': os.getenv('CORS_ORIGINS', '*').split(',')
    }