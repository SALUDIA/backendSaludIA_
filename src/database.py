from flask import Blueprint
import mysql.connector
from mysql.connector import Error
from config.loader import get_db_config
import logging

# Crear Blueprint para database
database_bp = Blueprint('database', __name__)

class DatabaseManager:
    def __init__(self):
        self.connection = None
        self.cursor = None
        
    def test_connection(self):
        """Probar conexión a la base de datos"""
        try:
            print("🔍 Probando conexión a base de datos...")
            
            db_config = get_db_config()
            
            # Configuración limpia para conexión
            connection_config = {
                'host': db_config['host'],
                'user': db_config['user'],
                'password': db_config['password'],
                'database': db_config['database'],
                'port': db_config['port'],
                'charset': db_config.get('charset', 'utf8mb4'),
                'autocommit': True,
                'connect_timeout': 30
            }
            
            # SSL para Aiven
            if 'aivencloud.com' in db_config['host']:
                connection_config.update({
                    'ssl_disabled': False,
                    'ssl_verify_cert': False,
                    'ssl_verify_identity': False
                })
                print("🔒 SSL habilitado para Aiven")
            else:
                connection_config['ssl_disabled'] = True
                print("🔓 SSL deshabilitado para BD local")
            
            print(f"🔗 Conectando a: {db_config['host']}:{db_config['port']}")
            
            # Probar conexión
            connection = mysql.connector.connect(**connection_config)
            
            if connection.is_connected():
                # Obtener info del servidor
                db_info = connection.get_server_info()
                cursor = connection.cursor()
                cursor.execute("SELECT DATABASE();")
                db_name = cursor.fetchone()[0]
                
                print(f"✅ Conectado a MySQL {db_info}")
                print(f"📊 Base de datos: {db_name}")
                
                cursor.close()
                connection.close()
                
                return True
            else:
                print("❌ Conexión fallida")
                return False
                
        except Error as e:
            print(f"❌ Error MySQL: {e}")
            return False
        except Exception as e:
            print(f"❌ Error general: {e}")
            return False

# Instancia global
db_manager = DatabaseManager()