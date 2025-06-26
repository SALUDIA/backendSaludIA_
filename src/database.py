import mysql.connector
from mysql.connector import Error
from src.config import Config
import logging
from datetime import datetime

class DatabaseManager:
    """Gestor simplificado de base de datos"""
    
    def __init__(self):
        self.connection = None
    
    def connect(self):
        """Conectar a la base de datos"""
        try:
            config = Config.get_db_config()
            self.connection = mysql.connector.connect(**config)
            return True
        except Error as e:
            logging.error(f"Error conectando a BD: {e}")
            return False
    
    def disconnect(self):
        """Desconectar de la base de datos"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
    
    def log_prediction(self, symptoms, diagnosis, confidence, model_version):
        """Registrar predicción en BD"""
        if not self.connect():
            return False
        
        try:
            cursor = self.connection.cursor()
            query = """
                INSERT INTO predictions (symptoms, diagnosis, confidence, model_version, timestamp)
                VALUES (%s, %s, %s, %s, %s)
            """
            values = (symptoms, diagnosis, confidence, model_version, datetime.now())
            cursor.execute(query, values)
            self.connection.commit()
            return True
            
        except Error as e:
            logging.error(f"Error guardando predicción: {e}")
            return False
        finally:
            self.disconnect()

# Instancia global
db_manager = DatabaseManager()