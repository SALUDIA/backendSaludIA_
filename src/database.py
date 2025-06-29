import mysql.connector
from mysql.connector import Error
from src.config import Config
import logging
from datetime import datetime
import numpy as np

class DatabaseManager:
    """Gestor mejorado de base de datos para Aiven"""
    
    def __init__(self):
        self.connection = None
        # Imprimir configuración al inicializar
        Config.print_config()
    
    def connect(self):
        """Conectar a la base de datos con manejo de SSL"""
        try:
            config = Config.get_db_config()
            
            print(f"🔌 Intentando conectar a BD:")
            print(f"   Host: {config['host']}:{config['port']}")
            print(f"   Usuario: {config['user']}")
            print(f"   Base: {config['database']}")
            print(f"   SSL: {'Habilitado' if not config.get('ssl_disabled', True) else 'Deshabilitado'}")
            
            self.connection = mysql.connector.connect(**config)
            
            if self.connection.is_connected():
                server_info = self.connection.get_server_info()
                print(f"✅ Conexión a BD exitosa - MySQL Server {server_info}")
                return True
                
        except Error as e:
            print(f"❌ Error conectando a BD: {e}")
            logging.error(f"❌ Error conectando a BD: {e}")
            return False
        
        return False
    
    def disconnect(self):
        """Desconectar de la base de datos"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔌 Desconectado de BD")
    
    def test_connection(self):
        """Probar conexión a la base de datos"""
        try:
            if self.connect():
                cursor = self.connection.cursor()
                cursor.execute("SELECT VERSION() as version, NOW() as current_time")
                result = cursor.fetchone()
                cursor.close()
                self.disconnect()
                
                return {
                    "status": "success", 
                    "message": "Conexión exitosa", 
                    "mysql_version": result[0],
                    "current_time": result[1].isoformat() if result[1] else None
                }
        except Exception as e:
            return {
                "status": "error", 
                "message": str(e)
            }
    
    def _convert_to_mysql_type(self, value):
        """Convertir tipos de Python/NumPy a tipos compatibles con MySQL"""
        if value is None:
            return None
        
        # Convertir numpy types a tipos nativos de Python
        if isinstance(value, np.integer):
            return int(value)
        elif isinstance(value, np.floating):
            return float(value)
        elif isinstance(value, np.str_):
            return str(value)
        elif isinstance(value, (list, tuple)):
            return str(value)  # Convertir listas/tuplas a string
        elif isinstance(value, dict):
            return str(value)  # Convertir diccionarios a string
        elif hasattr(value, 'item'):  # Para numpy scalars
            return value.item()
        
        # Para strings, asegurar que no sean demasiado largos
        if isinstance(value, str):
            if len(value) > 1000:
                return value[:1000] + "..."
            return value
        
        # Para números, convertir a tipos básicos
        if isinstance(value, (int, float)):
            return value
        
        # Para cualquier otro tipo, convertir a string
        return str(value)
    
    def log_prediction(self, symptoms, diagnosis, confidence, model_version, 
                      age_detected=None, age_range=None, gender=None, 
                      gender_origin=None, symptoms_processed=None):
        """Registrar predicción en BD con conversión de tipos"""
        if not self.connect():
            print("⚠️ No se pudo conectar a BD para logging")
            return False
        
        try:
            cursor = self.connection.cursor()
            
            # Convertir TODOS los valores a tipos compatibles con MySQL
            symptoms_clean = self._convert_to_mysql_type(symptoms)
            diagnosis_clean = self._convert_to_mysql_type(diagnosis)
            confidence_clean = self._convert_to_mysql_type(confidence)
            model_version_clean = self._convert_to_mysql_type(model_version)
            age_detected_clean = self._convert_to_mysql_type(age_detected)
            age_range_clean = self._convert_to_mysql_type(age_range)
            gender_clean = self._convert_to_mysql_type(gender)
            gender_origin_clean = self._convert_to_mysql_type(gender_origin)
            symptoms_processed_clean = self._convert_to_mysql_type(symptoms_processed)
            
            query = """
                INSERT INTO predictions 
                (symptoms, diagnosis, confidence, model_version, age_detected, 
                 age_range, gender, gender_origin, symptoms_processed, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                symptoms_clean, diagnosis_clean, confidence_clean, model_version_clean,
                age_detected_clean, age_range_clean, gender_clean, gender_origin_clean,
                symptoms_processed_clean, datetime.now()
            )
            
            cursor.execute(query, values)
            self.connection.commit()
            cursor.close()
            print(f"✅ Predicción guardada: {diagnosis_clean} ({confidence_clean}%)")
            return True
            
        except Error as e:
            logging.error(f"Error guardando predicción: {e}")
            print(f"❌ Error guardando predicción: {e}")
            return False
        finally:
            self.disconnect()
    
    def get_recommendations(self, diagnosis_name):
        """Obtener recomendaciones de la BD por diagnóstico"""
        if not self.connect():
            print("⚠️ No se pudo conectar a BD para recomendaciones")
            return []
        
        try:
            cursor = self.connection.cursor()
            
            # Limpiar y convertir el nombre del diagnóstico
            diagnosis_clean = self._convert_to_mysql_type(diagnosis_name)
            print(f"🔍 Buscando recomendaciones para: '{diagnosis_clean}'")
            
            query = """
                SELECT r.recommendation_text, r.category, r.priority
                FROM recommendations r
                JOIN diagnoses d ON r.diagnosis_id = d.id
                WHERE (d.name_en = %s OR d.name_es = %s) 
                AND r.is_active = TRUE
                ORDER BY r.priority ASC, r.id ASC
            """
            cursor.execute(query, (diagnosis_clean, diagnosis_clean))
            recommendations = cursor.fetchall()
            cursor.close()
            
            # Convertir a lista de strings
            result = [self._convert_to_mysql_type(rec[0]) for rec in recommendations]
            print(f"✅ Encontradas {len(result)} recomendaciones para '{diagnosis_clean}'")
            return result
            
        except Error as e:
            logging.error(f"Error obteniendo recomendaciones: {e}")
            print(f"❌ Error obteniendo recomendaciones: {e}")
            return []
        finally:
            self.disconnect()

# Instancia global
db_manager = DatabaseManager()