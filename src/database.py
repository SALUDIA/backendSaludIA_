import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime
import json
from contextlib import contextmanager
from config.loader import get_db_config

class DatabaseManager:
    def __init__(self):
        self.config = get_db_config()
        
        # 🔍 DEBUG: Mostrar configuración (sin password)
        env = os.getenv('FLASK_ENV', 'development')
        print(f"🔧 Entorno: {env}")
        
        if env == 'development':
            host = self.config.get('host', 'No configurado')
            print(f"🔗 Conectando a: {host}")
            
            # Si es localhost y no tiene password, advertir
            if host == 'localhost' and not self.config.get('password'):
                print("⚠️ MySQL local sin password detectado")
                print("💡 Configura LOCAL_DB_PASSWORD en .env")
        
        # DICCIONARIO DE TRADUCCIÓN DE ENFERMEDADES
        self.disease_translations = {
            # Enfermedades específicas del modelo v9
            'Fungal infection': 'Infección por Hongos',
            'Allergy': 'Alergia',
            'GERD': 'Reflujo Gastroesofágico',
            'Chronic cholestasis': 'Colestasis Crónica',
            'Drug Reaction': 'Reacción a Medicamentos',
            'Peptic ulcer diseae': 'Enfermedad de Úlcera Péptica',
            'AIDS': 'SIDA',
            'Diabetes': 'Diabetes',
            'Gastroenteritis': 'Gastroenteritis',
            'Bronchial Asthma': 'Asma Bronquial',
            'Hypertension': 'Hipertensión',
            'Migraine': 'Migraña',
            'Cervical spondylosis': 'Espondilosis Cervical',
            'Paralysis (brain hemorrhage)': 'Parálisis (Hemorragia Cerebral)',
            'Jaundice': 'Ictericia',
            'Malaria': 'Malaria',
            'Chicken pox': 'Varicela',
            'Dengue': 'Dengue',
            'Typhoid': 'Tifoidea',
            'hepatitis A': 'Hepatitis A',
            'Hepatitis B': 'Hepatitis B',
            'Hepatitis C': 'Hepatitis C',
            'Hepatitis D': 'Hepatitis D',
            'Hepatitis E': 'Hepatitis E',
            'Alcoholic hepatitis': 'Hepatitis Alcohólica',
            'Tuberculosis': 'Tuberculosis',
            'Common Cold': 'Resfriado Común',
            'Pneumonia': 'Neumonía',
            'Dimorphic hemmorhoids(piles)': 'Hemorroides',
            'Heart attack': 'Infarto Cardíaco',
            'Varicose veins': 'Várices',
            'Hypothyroidism': 'Hipotiroidismo',
            'Hyperthyroidism': 'Hipertiroidismo',
            'Hypoglycemia': 'Hipoglucemia',
            'Osteoarthristis': 'Osteoartritis',
            'Arthritis': 'Artritis',
            '(vertigo) Paroymsal  Positional Vertigo': 'Vértigo Posicional',
            'Acne': 'Acné',
            'Urinary tract infection': 'Infección del Tracto Urinario',
            'Psoriasis': 'Psoriasis',
            'Impetigo': 'Impétigo',
            
            # Categorías generales del modelo v7/v8
            'Cardiac/Circulatory': 'Cardiaco/Circulatorio',
            'Digestive System/ Gastrointestinal': 'Sistema Digestivo/Gastrointestinal',
            'Ears, Nose, Throat': 'Oídos, Nariz, Garganta',
            'Endocrine/ Metabolic': 'Endocrino/Metabólico',
            'Genitourinary': 'Genitourinario',
            'Infectious': 'Infeccioso',
            'Mental': 'Mental',
            'Musculoskeletal': 'Musculoesquelético',
            'Orthopedic/ Musculoskeletal': 'Ortopédico/Musculoesquelético',
            'Central Nervous System/ Neuromuscular': 'Sistema Nervioso Central/Neuromuscular',
            'Respiratory': 'Respiratorio',
            'Skin/ Dermatologic': 'Piel/Dermatológico',
            'Vision': 'Visión',
            'Cancer': 'Cáncer',
            'Blood': 'Sangre',
            'Pregnancy': 'Embarazo',
            'Pediatric': 'Pediátrico',
        }
    
    def translate_disease(self, disease_name):
        """Traducir nombre de enfermedad al español"""
        return self.disease_translations.get(disease_name, disease_name)
    
    @contextmanager
    def get_connection(self):
        """Context manager para conexiones de BD con manejo de errores mejorado"""
        connection = None
        try:
            # 🔧 Configuración SSL según entorno
            ssl_config = {}
            if os.getenv('FLASK_ENV') == 'production' or 'aivencloud.com' in str(self.config.get('host', '')):
                ssl_config = {
                    'ssl_disabled': False,
                    'ssl_verify_cert': False,
                    'ssl_verify_identity': False
                }
            
            # Combinar configuración
            connection_config = {**self.config, **ssl_config}
            
            # 🔍 DEBUG: Mostrar intento de conexión (sin password)
            debug_config = {k: v for k, v in connection_config.items() if 'password' not in k.lower()}
            print(f"🔗 Intentando conectar: {debug_config}")
            
            connection = mysql.connector.connect(**connection_config)
            yield connection
            
        except Error as e:
            if connection:
                connection.rollback()
            
            # 🔍 Manejo de errores específicos
            if e.errno == 1045:  # Access denied
                print(f"❌ Error de autenticación MySQL:")
                print(f"   Host: {self.config.get('host')}")
                print(f"   User: {self.config.get('user')}")
                print(f"   Database: {self.config.get('database')}")
                print(f"💡 Verifica credenciales en .env")
            elif e.errno == 2003:  # Can't connect
                print(f"❌ No se puede conectar al servidor MySQL:")
                print(f"   Host: {self.config.get('host')}:{self.config.get('port')}")
                print(f"💡 Verifica que MySQL esté ejecutándose")
            else:
                print(f"❌ Error de conexión BD: {e}")
            
            raise e
        finally:
            if connection and connection.is_connected():
                connection.close()
    
    def test_connection(self):
        """Probar conexión a la base de datos con diagnóstico detallado"""
        try:
            print("🔍 Probando conexión a base de datos...")
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                cursor.close()
                print("✅ Conexión exitosa")
                return True
        except Error as e:
            print(f"❌ Error de conexión: {e}")
            
            # Sugerencias según el error
            if e.errno == 1045:
                print("🔧 SOLUCIONES POSIBLES:")
                print("   1. Configurar password en LOCAL_DB_PASSWORD")
                print("   2. Crear usuario MySQL: CREATE USER 'root'@'localhost' IDENTIFIED BY 'password';")
                print("   3. Usar usuario diferente en LOCAL_DB_USER")
            elif e.errno == 2003:
                print("🔧 SOLUCIONES POSIBLES:")
                print("   1. Instalar MySQL: https://dev.mysql.com/downloads/mysql/")
                print("   2. Iniciar servicio MySQL")
                print("   3. Verificar puerto en LOCAL_DB_PORT")
            
            return False
    
    def _convert_numpy_types(self, data):
        """🔧 CONVERTIR TIPOS DE NUMPY A TIPOS PYTHON ESTÁNDAR"""
        if hasattr(data, 'item'):  # numpy scalars
            return data.item()
        elif hasattr(data, 'tolist'):  # numpy arrays
            return data.tolist()
        elif isinstance(data, (list, tuple)):
            return [self._convert_numpy_types(item) for item in data]
        elif isinstance(data, dict):
            return {key: self._convert_numpy_types(value) for key, value in data.items()}
        else:
            return data
    
    def save_consultation(self, data):
        """Guardar consulta médica con conversión de tipos"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Crear tabla si no existe (solo para desarrollo)
                if os.getenv('FLASK_ENV') == 'development':
                    self._create_tables_if_not_exist(cursor)
                
                # 🔧 CONVERTIR TIPOS DE DATOS ANTES DE INSERTAR
                clean_data = {}
                for key, value in data.items():
                    clean_data[key] = self._convert_numpy_types(value)
                
                # 🔧 ASEGURAR TIPOS CORRECTOS
                query = """
                INSERT INTO consultations 
                (session_id, symptoms_original, symptoms_processed, age_range, 
                 gender, main_diagnosis, confidence_score, confidence_level, 
                 model_version, ip_address, user_agent)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                
                # Convertir explícitamente los valores
                values = (
                    str(clean_data.get('session_id', '')),
                    str(clean_data.get('symptoms_original', '')),
                    str(clean_data.get('symptoms_processed', '')),
                    str(clean_data.get('age_range', '')),
                    str(clean_data.get('gender', '')),
                    str(clean_data.get('main_diagnosis', '')),
                    float(clean_data.get('confidence_score', 0)) if clean_data.get('confidence_score') is not None else None,
                    str(clean_data.get('confidence_level', '')),
                    str(clean_data.get('model_version', 'v8')),
                    str(clean_data.get('ip_address', '')),
                    str(clean_data.get('user_agent', ''))
                )
                
                # 🔍 DEBUG: Mostrar tipos de datos
                if os.getenv('LOG_LEVEL') == 'DEBUG':
                    print("🔍 Tipos de datos para BD:")
                    for i, val in enumerate(values):
                        print(f"   {i}: {type(val).__name__} = {val}")
                
                cursor.execute(query, values)
                
                consultation_id = cursor.lastrowid
                conn.commit()
                cursor.close()
                
                print(f"✅ Consulta guardada con ID: {consultation_id}")
                return consultation_id
                
        except Error as e:
            print(f"❌ Error guardando consulta: {e}")
            print(f"🔍 Error específico: {e.msg if hasattr(e, 'msg') else str(e)}")
            return None
        except Exception as e:
            print(f"❌ Error inesperado guardando consulta: {e}")
            print(f"🔍 Tipo de error: {type(e).__name__}")
            return None
    
    def save_predictions(self, consultation_id, predictions):
        """Guardar predicciones top N con conversión de tipos"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                query = """
                INSERT INTO predictions (consultation_id, disease_name, probability, ranking)
                VALUES (%s, %s, %s, %s)
                """
                
                for rank, pred in enumerate(predictions, 1):
                    # 🔧 CONVERTIR TIPOS EXPLÍCITAMENTE
                    values = (
                        int(consultation_id),
                        str(pred['disease']),
                        float(self._convert_numpy_types(pred['probability'])),
                        int(rank)
                    )
                    
                    cursor.execute(query, values)
                
                conn.commit()
                cursor.close()
                print(f"✅ {len(predictions)} predicciones guardadas")
                return True
                
        except Error as e:
            print(f"❌ Error guardando predicciones: {e}")
            return False
        except Exception as e:
            print(f"❌ Error inesperado guardando predicciones: {e}")
            return False
    
    def get_consultation_stats(self):
        """Obtener estadísticas de consultas"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor(dictionary=True)
                
                # Consultas por modelo
                cursor.execute("""
                    SELECT model_version, COUNT(*) as count
                    FROM consultations
                    GROUP BY model_version
                    ORDER BY count DESC
                """)
                model_stats = cursor.fetchall()
                
                # Diagnósticos más comunes
                cursor.execute("""
                    SELECT main_diagnosis, COUNT(*) as count
                    FROM consultations
                    WHERE main_diagnosis IS NOT NULL
                    GROUP BY main_diagnosis
                    ORDER BY count DESC
                    LIMIT 10
                """)
                diagnosis_stats = cursor.fetchall()
                
                # Total de consultas
                cursor.execute("SELECT COUNT(*) as total FROM consultations")
                total = cursor.fetchone()['total']
                
                cursor.close()
                
                return {
                    'total_consultations': total,
                    'model_usage': model_stats,
                    'top_diagnoses': diagnosis_stats
                }
                
        except Error as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            return None
    
    def _create_tables_if_not_exist(self, cursor):
        """Crear tablas si no existen (solo desarrollo)"""
        try:
            print("🔧 Creando tablas si no existen...")
            
            # Tabla consultations
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS consultations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    session_id VARCHAR(255) NOT NULL,
                    symptoms_original TEXT NOT NULL,
                    symptoms_processed TEXT,
                    symptoms_translated TEXT,
                    age_original INT,
                    age_range VARCHAR(50),
                    gender_original VARCHAR(50),
                    gender VARCHAR(50),
                    main_diagnosis VARCHAR(255),
                    confidence_score DECIMAL(5,2),
                    confidence_level VARCHAR(50),
                    model_version VARCHAR(50) NOT NULL DEFAULT 'v8',
                    detected_language VARCHAR(10),
                    ip_address VARCHAR(45),
                    user_agent TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_session (session_id),
                    INDEX idx_diagnosis (main_diagnosis),
                    INDEX idx_model (model_version),
                    INDEX idx_created (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabla predictions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS predictions (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    consultation_id INT NOT NULL,
                    disease_name VARCHAR(255) NOT NULL,
                    probability DECIMAL(5,2) NOT NULL,
                    ranking INT NOT NULL DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (consultation_id) REFERENCES consultations(id) ON DELETE CASCADE,
                    INDEX idx_consultation (consultation_id),
                    INDEX idx_disease (disease_name),
                    INDEX idx_probability (probability DESC)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabla system_logs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    level ENUM('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL') NOT NULL DEFAULT 'INFO',
                    message TEXT NOT NULL,
                    module VARCHAR(100),
                    user_id VARCHAR(255),
                    ip_address VARCHAR(45),
                    additional_data JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_level (level),
                    INDEX idx_module (module),
                    INDEX idx_created (created_at)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            print("✅ Tablas creadas/verificadas correctamente")
            
        except Error as e:
            print(f"⚠️ Error creando tablas: {e}")

# Instancia global
db_manager = DatabaseManager()