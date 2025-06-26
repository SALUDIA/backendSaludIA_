import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración simple y directa"""
    
    # Base de datos
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'saludiadb')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    
    # Modelos
    MODELS_DIR = 'models'
    
    # API
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
    
    @staticmethod
    def get_db_config():
        """Retorna configuración de BD"""
        return {
            'host': Config.DB_HOST,
            'user': Config.DB_USER,
            'password': Config.DB_PASSWORD,
            'database': Config.DB_NAME,
            'port': Config.DB_PORT
        }