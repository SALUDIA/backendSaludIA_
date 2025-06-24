import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def get_config_instance():
    """Obtener instancia de configuración según el entorno"""
    env = os.getenv('FLASK_ENV', 'development')
    
    if env == 'production':
        from .production import ProductionConfig
        config = ProductionConfig()
    elif env == 'testing':
        from .testing import TestingConfig
        config = TestingConfig()
    else:
        from .development import DevelopmentConfig
        config = DevelopmentConfig()
    
    print(f"🔧 Configuración cargada: {config.__class__.__name__}")
    return config

def get_db_config():
    """Obtener configuración específica de base de datos según entorno"""
    env = os.getenv('FLASK_ENV', 'development')
    force_aiven = os.getenv('FORCE_AIVEN', 'false').lower() == 'true'
    
    if env == 'production' or force_aiven:
        # 🌐 CONEXIÓN A AIVEN (PRODUCCIÓN)
        print("🌐 Usando base de datos AIVEN para producción")
        return {
            'host': os.getenv('DB_HOST'),
            'port': int(os.getenv('DB_PORT', 28633)),
            'user': os.getenv('DB_USER'),
            'password': os.getenv('DB_PASSWORD'),
            'database': os.getenv('DB_NAME', 'defaultdb'),
            'charset': 'utf8mb4',
            'use_unicode': True,
            'autocommit': True,
            
            # 🔒 SSL REQUERIDO PARA AIVEN
            'ssl_disabled': False,
            'ssl_verify_cert': os.getenv('DB_SSL_VERIFY_CERT', 'false').lower() == 'true',
            'ssl_verify_identity': os.getenv('DB_SSL_VERIFY_IDENTITY', 'false').lower() == 'true',
            
            # Pool optimizado para producción
            'pool_name': 'saludia_aiven_pool',
            'pool_size': int(os.getenv('DB_POOL_SIZE', 5)),
            'pool_reset_session': True,
            'connection_timeout': int(os.getenv('DB_POOL_TIMEOUT', 30))
        }
    elif env == 'testing':
        # Testing con Aiven o local según configuración
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 28633 if os.getenv('DB_HOST') else 3306)),
            'user': os.getenv('DB_USER', 'root'),
            'password': os.getenv('DB_PASSWORD', ''),
            'database': os.getenv('DB_NAME', 'defaultdb' if os.getenv('DB_HOST') else 'saludiadb_test'),
            'charset': 'utf8mb4',
            'use_unicode': True,
            'autocommit': True,
            
            # SSL solo si es Aiven
            'ssl_disabled': False if 'aivencloud.com' in os.getenv('DB_HOST', '') else True,
            'ssl_verify_cert': False,
            'ssl_verify_identity': False
        }
    else:
        # 🏠 DESARROLLO: LOCAL PRIORITARIO, AIVEN COMO FALLBACK
        use_local = (
            os.getenv('LOCAL_DB_HOST') and 
            os.getenv('LOCAL_DB_USER') and
            not force_aiven
        )
        
        if use_local:
            print("🏠 Usando base de datos LOCAL para desarrollo")
            return {
                'host': os.getenv('LOCAL_DB_HOST', 'localhost'),
                'port': int(os.getenv('LOCAL_DB_PORT', 3306)),
                'user': os.getenv('LOCAL_DB_USER', 'root'),
                'password': os.getenv('LOCAL_DB_PASSWORD', ''),
                'database': os.getenv('LOCAL_DB_NAME', 'saludiadb'),
                'charset': 'utf8mb4',
                'use_unicode': True,
                'autocommit': True,
                'ssl_disabled': True  # Sin SSL para MySQL local
            }
        else:
            print("🌐 Usando base de datos AIVEN para desarrollo (fallback)")
            return {
                'host': os.getenv('DB_HOST'),
                'port': int(os.getenv('DB_PORT', 28633)),
                'user': os.getenv('DB_USER'),
                'password': os.getenv('DB_PASSWORD'),
                'database': os.getenv('DB_NAME', 'defaultdb'),
                'charset': 'utf8mb4',
                'use_unicode': True,
                'autocommit': True,
                
                # SSL requerido para Aiven
                'ssl_disabled': False,
                'ssl_verify_cert': False,
                'ssl_verify_identity': False
            }

def get_cors_config():
    """Obtener configuración CORS"""
    origins = os.getenv('CORS_ORIGINS', '*')
    if origins == '*':
        return {
            'origins': ['*'],
            'methods': os.getenv('CORS_METHODS', 'GET,POST,PUT,DELETE,OPTIONS').split(','),
            'allow_headers': os.getenv('CORS_ALLOW_HEADERS', 'Content-Type,Authorization,X-Requested-With').split(','),
            'supports_credentials': os.getenv('CORS_SUPPORTS_CREDENTIALS', 'false').lower() == 'true'
        }
    else:
        return {
            'origins': origins.split(','),
            'methods': os.getenv('CORS_METHODS', 'GET,POST,PUT,DELETE,OPTIONS').split(','),
            'allow_headers': os.getenv('CORS_ALLOW_HEADERS', 'Content-Type,Authorization,X-Requested-With').split(','),
            'supports_credentials': os.getenv('CORS_SUPPORTS_CREDENTIALS', 'true').lower() == 'true'
        }

def validate_environment():
    """Validar que todas las variables críticas estén configuradas"""
    required_vars = {
        'production': ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'SECRET_KEY', 'JWT_SECRET_KEY'],
        'development': ['SECRET_KEY', 'JWT_SECRET_KEY'],
        'testing': ['SECRET_KEY', 'JWT_SECRET_KEY']
    }
    
    env = os.getenv('FLASK_ENV', 'development')
    missing_vars = []
    
    for var in required_vars.get(env, []):
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variables críticas faltantes para {env}: {missing_vars}")
        return False
    else:
        print(f"✅ Todas las variables críticas configuradas para {env}")
        return True

# Validar al importar
if __name__ != '__main__':
    validate_environment()