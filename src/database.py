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
        self.config = Config.get_db_config()
    
    def connect(self):
        """Conectar a la base de datos con manejo de SSL"""
        try:
            self.connection = mysql.connector.connect(**self.config)
            if self.connection.is_connected():
                print(f"✅ Conectado a BD: {self.config['host']}:{self.config['port']}")
                return True
        except Error as e:
            logging.error(f"❌ Error conectando a BD: {e}")
            print(f"❌ Error conectando a BD: {e}")
            return False
    
    def disconnect(self):
        """Desconectar de la base de datos"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("🔌 Desconectado de BD")
    
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
    
    def test_connection(self):
        """Probar conexión a la base de datos"""
        try:
            if self.connect():
                cursor = self.connection.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                cursor.close()
                self.disconnect()
                return {"status": "success", "message": "Conexión exitosa", "result": result}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    def create_tables(self):
        """Crear tablas necesarias"""
        if not self.connect():
            return False
        
        try:
            cursor = self.connection.cursor()
            
            # Tabla de predicciones
            create_predictions = """
            CREATE TABLE IF NOT EXISTS predictions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                symptoms TEXT,
                diagnosis VARCHAR(255),
                confidence DECIMAL(5,2),
                model_version VARCHAR(50),
                age_detected INT,
                age_range VARCHAR(20),
                gender VARCHAR(20),
                gender_origin VARCHAR(20),
                symptoms_processed TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
            
            # Tabla de diagnósticos
            create_diagnoses = """
            CREATE TABLE IF NOT EXISTS diagnoses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name_en VARCHAR(255) NOT NULL UNIQUE,
                name_es VARCHAR(255) NOT NULL,
                description_es TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
            
            # Tabla de recomendaciones
            create_recommendations = """
            CREATE TABLE IF NOT EXISTS recommendations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                diagnosis_id INT NOT NULL,
                recommendation_text TEXT NOT NULL,
                category VARCHAR(100),
                priority INT DEFAULT 1,
                is_active BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (diagnosis_id) REFERENCES diagnoses(id) ON DELETE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """
            
            cursor.execute(create_predictions)
            cursor.execute(create_diagnoses)
            cursor.execute(create_recommendations)
            
            self.connection.commit()
            cursor.close()
            print("✅ Tablas creadas exitosamente")
            return True
            
        except Error as e:
            logging.error(f"Error creando tablas: {e}")
            print(f"❌ Error creando tablas: {e}")
            return False
        finally:
            self.disconnect()
    
    def log_prediction(self, symptoms, diagnosis, confidence, model_version, 
                      age_detected=None, age_range=None, gender=None, 
                      gender_origin=None, symptoms_processed=None):
        """Registrar predicción en BD con conversión de tipos"""
        if not self.connect():
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
            
            # Debug: mostrar tipos convertidos
            print(f"🔧 Tipos convertidos:")
            print(f"   symptoms: {type(symptoms_clean)} = {symptoms_clean[:50] if symptoms_clean else None}...")
            print(f"   diagnosis: {type(diagnosis_clean)} = {diagnosis_clean}")
            print(f"   confidence: {type(confidence_clean)} = {confidence_clean}")
            print(f"   model_version: {type(model_version_clean)} = {model_version_clean}")
            print(f"   age_detected: {type(age_detected_clean)} = {age_detected_clean}")
            print(f"   age_range: {type(age_range_clean)} = {age_range_clean}")
            print(f"   gender: {type(gender_clean)} = {gender_clean}")
            print(f"   gender_origin: {type(gender_origin_clean)} = {gender_origin_clean}")
            
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
            print(f"❌ Valores que causaron error: {values}")
            return False
        finally:
            self.disconnect()
    
    def get_recommendations(self, diagnosis_name):
        """Obtener recomendaciones de la BD por diagnóstico"""
        if not self.connect():
            return []
        
        try:
            cursor = self.connection.cursor()
            
            # Limpiar y convertir el nombre del diagnóstico
            diagnosis_clean = self._convert_to_mysql_type(diagnosis_name)
            print(f"🔍 Buscando recomendaciones para: '{diagnosis_clean}' (tipo: {type(diagnosis_clean)})")
            
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
            print(f"❌ Diagnóstico que causó error: {diagnosis_name} (tipo: {type(diagnosis_name)})")
            return []
        finally:
            self.disconnect()
    
    def seed_diagnoses_and_recommendations(self):
        """Poblar BD con diagnósticos y recomendaciones"""
        if not self.connect():
            return False
        
        try:
            cursor = self.connection.cursor()
            
            # Limpiar datos existentes (opcional - descomenta si necesitas resetear)
            # cursor.execute("DELETE FROM recommendations WHERE id > 0")
            # cursor.execute("DELETE FROM diagnoses WHERE id > 0")
            
            # Datos de diagnósticos y recomendaciones
            diagnoses_data = [
                ("Diabetes", "Diabetes", "Enfermedad metabólica caracterizada por niveles altos de glucosa"),
                ("Hypertension", "Hipertensión", "Presión arterial elevada de forma persistente"),
                ("Migraine", "Migraña", "Tipo de dolor de cabeza recurrente e intenso"),
                ("Asthma", "Asma", "Enfermedad respiratoria crónica"),
                ("Gastroenteritis", "Gastroenteritis", "Inflamación del tracto gastrointestinal"),
                ("Bronchitis", "Bronquitis", "Inflamación de los bronquios"),
                ("Arthritis", "Artritis", "Inflamación de las articulaciones"),
                ("Allergy", "Alergia", "Reacción del sistema inmunitario a sustancias"),
                ("Pneumonia", "Neumonía", "Infección pulmonar"),
                ("Urinary tract infection", "Infección del tracto urinario", "Infección en el sistema urinario"),
                ("Central Nervous System/ Neuromuscular", "Sistema Nervioso Central/Neuromuscular", "Trastornos del sistema nervioso"),
                ("Musculoskeletal", "Musculoesquelético", "Trastornos de músculos y huesos"),
                ("Cardiovascular", "Cardiovascular", "Trastornos del corazón y vasos sanguíneos"),
                ("Respiratory", "Respiratorio", "Trastornos del sistema respiratorio"),
                ("Gastrointestinal", "Gastrointestinal", "Trastornos del sistema digestivo")
            ]
            
            # Insertar diagnósticos
            for name_en, name_es, description in diagnoses_data:
                try:
                    cursor.execute("""
                        INSERT INTO diagnoses (name_en, name_es, description_es)
                        VALUES (%s, %s, %s)
                        ON DUPLICATE KEY UPDATE
                        name_es = VALUES(name_es),
                        description_es = VALUES(description_es)
                    """, (name_en, name_es, description))
                except Error as e:
                    if "Duplicate entry" not in str(e):
                        print(f"Error insertando {name_en}: {e}")
            
            # Recomendaciones por diagnóstico
            recommendations_data = {
                "Diabetes": [
                    ("Controla regularmente tus niveles de glucosa", "medical", 1),
                    ("Mantén una dieta balanceada baja en azúcares", "lifestyle", 2),
                    ("Realiza ejercicio moderado regularmente", "lifestyle", 3)
                ],
                "Hypertension": [
                    ("Reduce el consumo de sal en tu dieta", "diet", 1),
                    ("Controla tu presión arterial regularmente", "monitoring", 2),
                    ("Evita el estrés y practica técnicas de relajación", "lifestyle", 3)
                ],
                "Migraine": [
                    ("Identifica y evita los desencadenantes de dolor", "prevention", 1),
                    ("Mantén horarios regulares de sueño", "lifestyle", 2),
                    ("Considera técnicas de manejo del estrés", "lifestyle", 3)
                ],
                "Asthma": [
                    ("Evita los desencadenantes conocidos", "prevention", 1),
                    ("Mantén tu inhalador siempre disponible", "medical", 2),
                    ("Realiza ejercicios de respiración", "lifestyle", 3)
                ],
                "Central Nervous System/ Neuromuscular": [
                    ("Mantén un estilo de vida activo y saludable", "lifestyle", 1),
                    ("Evita factores que puedan empeorar los síntomas", "prevention", 2),
                    ("Busca evaluación neurológica especializada", "medical", 3),
                    ("Considera terapias de rehabilitación física", "treatment", 4)
                ],
                "Musculoskeletal": [
                    ("Mantén una postura correcta", "lifestyle", 1),
                    ("Realiza ejercicios de fortalecimiento", "exercise", 2),
                    ("Aplica terapias de calor o frío según sea necesario", "treatment", 3)
                ],
                "Gastroenteritis": [
                    ("Mantente hidratado bebiendo líquidos claros", "hydration", 1),
                    ("Come alimentos blandos y fáciles de digerir", "diet", 2),
                    ("Evita lácteos y alimentos grasos temporalmente", "diet", 3)
                ],
                "Pneumonia": [
                    ("Descansa completamente y evita esfuerzos físicos", "rest", 1),
                    ("Mantente bien hidratado", "hydration", 2),
                    ("Busca atención médica inmediata si empeoran los síntomas", "medical", 3)
                ]
            }
            
            # Insertar recomendaciones
            for diagnosis_name, recs in recommendations_data.items():
                # Obtener ID del diagnóstico
                cursor.execute("SELECT id FROM diagnoses WHERE name_en = %s", (diagnosis_name,))
                diagnosis_result = cursor.fetchone()
                if diagnosis_result:
                    diagnosis_id = diagnosis_result[0]
                    for rec_text, category, priority in recs:
                        try:
                            cursor.execute("""
                                INSERT INTO recommendations 
                                (diagnosis_id, recommendation_text, category, priority)
                                VALUES (%s, %s, %s, %s)
                                ON DUPLICATE KEY UPDATE
                                recommendation_text = VALUES(recommendation_text),
                                category = VALUES(category),
                                priority = VALUES(priority)
                            """, (diagnosis_id, rec_text, category, priority))
                        except Error as e:
                            print(f"Error insertando recomendación para {diagnosis_name}: {e}")
            
            self.connection.commit()
            cursor.close()
            print("✅ Diagnósticos y recomendaciones insertados/actualizados")
            return True
            
        except Error as e:
            logging.error(f"Error poblando BD: {e}")
            print(f"❌ Error poblando BD: {e}")
            return False
        finally:
            self.disconnect()

# Instancia global
db_manager = DatabaseManager()