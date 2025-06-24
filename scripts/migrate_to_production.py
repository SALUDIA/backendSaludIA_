import os
import sys
from dotenv import load_dotenv

# 🔧 ARREGLAR PATH PARA IMPORTACIONES
# Obtener directorio del script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Obtener directorio Backend (un nivel arriba)
backend_dir = os.path.dirname(script_dir)
# Agregar Backend al path de Python
sys.path.insert(0, backend_dir)

# Cambiar al directorio Backend para que funcionen las rutas relativas
os.chdir(backend_dir)

# Cargar variables de entorno
load_dotenv()

def setup_production_database():
    """Configurar conexión a base de datos de producción (Aiven)"""
    
    print("🚀 CONFIGURANDO CONEXIÓN A BASE DE DATOS DE PRODUCCIÓN")
    print("=" * 60)
    
    # Mostrar directorio de trabajo
    print(f"📁 Directorio de trabajo: {os.getcwd()}")
    print(f"📁 Python path: {sys.path[0]}")
    
    # Verificar que tenemos las credenciales de Aiven
    required_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME', 'DB_PORT']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Variables faltantes: {missing_vars}")
        return False
    
    # Mostrar configuración (sin password)
    print("🔍 Configuración de producción:")
    print(f"   Host: {os.getenv('DB_HOST')}")
    print(f"   Puerto: {os.getenv('DB_PORT')}")
    print(f"   Usuario: {os.getenv('DB_USER')}")
    print(f"   Base de datos: {os.getenv('DB_NAME')}")
    print(f"   SSL requerido: {os.getenv('DB_SSL_REQUIRED', 'true')}")
    
    return True

def test_production_connection():
    """Probar conexión específica a producción"""
    try:
        # Forzar uso de Aiven incluso en desarrollo
        os.environ['FORCE_AIVEN'] = 'true'
        
        print("\n🔗 Probando conexión a Aiven MySQL...")
        print("📦 Importando módulos...")
        
        # Importar después de configurar variable y path
        try:
            from src.database import db_manager
            print("   ✅ src.database importado correctamente")
        except ImportError as e:
            print(f"   ❌ Error importando src.database: {e}")
            print(f"   📁 Contenido de src/: {os.listdir('src') if os.path.exists('src') else 'No existe'}")
            return False
        
        try:
            from config.loader import get_db_config
            print("   ✅ config.loader importado correctamente")
        except ImportError as e:
            print(f"   ❌ Error importando config.loader: {e}")
            print(f"   📁 Contenido de config/: {os.listdir('config') if os.path.exists('config') else 'No existe'}")
            return False
        
        # Mostrar configuración que se está usando
        db_config = get_db_config()
        print(f"🌐 Conectando a: {db_config.get('host')}:{db_config.get('port')}")
        print(f"📊 Base de datos: {db_config.get('database')}")
        print(f"🔒 SSL: {'Habilitado' if not db_config.get('ssl_disabled', True) else 'Deshabilitado'}")
        
        # Probar conexión
        success = db_manager.test_connection()
        
        if success:
            print("✅ ¡CONEXIÓN A PRODUCCIÓN EXITOSA!")
            
            # Crear tablas si no existen
            print("\n🔧 Verificando/creando tablas en producción...")
            try:
                with db_manager.get_connection() as conn:
                    cursor = conn.cursor()
                    db_manager._create_tables_if_not_exist(cursor)
                    cursor.close()
                print("✅ Tablas verificadas en producción")
            except Exception as e:
                print(f"⚠️ Error creando tablas: {e}")
            
            return True
        else:
            print("❌ Error de conexión a producción")
            return False
            
    except Exception as e:
        print(f"❌ Error probando conexión: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_production_tables():
    """Crear tablas específicamente en producción"""
    try:
        os.environ['FORCE_AIVEN'] = 'true'
        from src.database import db_manager
        
        print("\n🏗️ CREANDO TABLAS EN BASE DE DATOS DE PRODUCCIÓN")
        print("=" * 50)
        
        with db_manager.get_connection() as conn:
            cursor = conn.cursor()
            
            # Tabla consultations con todos los campos
            print("📋 Creando tabla consultations...")
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
                    INDEX idx_created (created_at),
                    INDEX idx_confidence (confidence_score DESC)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabla predictions
            print("🔮 Creando tabla predictions...")
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
                    INDEX idx_probability (probability DESC),
                    INDEX idx_ranking (ranking)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
            """)
            
            # Tabla system_logs
            print("📝 Creando tabla system_logs...")
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
            
            # Verificar tablas creadas
            print("\n🔍 Verificando tablas creadas...")
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            expected_tables = ['consultations', 'predictions', 'system_logs']
            created_tables = [table[0] for table in tables]
            
            for table in expected_tables:
                if table in created_tables:
                    print(f"   ✅ {table}")
                else:
                    print(f"   ❌ {table} (no creada)")
            
            cursor.close()
            
        print("✅ ¡TABLAS DE PRODUCCIÓN CREADAS EXITOSAMENTE!")
        return True
        
    except Exception as e:
        print(f"❌ Error creando tablas de producción: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_production_insert():
    """Probar inserción en base de datos de producción"""
    try:
        os.environ['FORCE_AIVEN'] = 'true'
        from src.database import db_manager
        from datetime import datetime
        
        print("\n🧪 PROBANDO INSERCIÓN EN PRODUCCIÓN")
        print("=" * 40)
        
        # Datos de prueba
        test_consultation = {
            'session_id': f'prod-test-{datetime.now().strftime("%Y%m%d-%H%M%S")}',
            'symptoms_original': 'Dolor de cabeza y fiebre - PRUEBA PRODUCCIÓN',
            'symptoms_processed': 'headache fever - production test',
            'age_range': '31-40',
            'gender': 'Male',
            'main_diagnosis': 'Test Diagnosis - Production',
            'confidence_score': 85.5,
            'confidence_level': 'Alta',
            'model_version': 'v8-prod-test',
            'detected_language': 'es',
            'ip_address': '127.0.0.1',
            'user_agent': 'Production Test Agent'
        }
        
        # Insertar consulta
        consultation_id = db_manager.save_consultation(test_consultation)
        
        if consultation_id:
            print(f"✅ Consulta insertada con ID: {consultation_id}")
            
            # Insertar predicciones de prueba
            test_predictions = [
                {'disease': 'Test Disease 1', 'probability': 85.5},
                {'disease': 'Test Disease 2', 'probability': 12.3},
                {'disease': 'Test Disease 3', 'probability': 2.2}
            ]
            
            predictions_success = db_manager.save_predictions(consultation_id, test_predictions)
            
            if predictions_success:
                print("✅ Predicciones insertadas correctamente")
                
                # Verificar datos insertados
                print("\n📊 Verificando datos insertados...")
                with db_manager.get_connection() as conn:
                    cursor = conn.cursor(dictionary=True)
                    
                    # Consultar consulta insertada
                    cursor.execute("SELECT * FROM consultations WHERE id = %s", (consultation_id,))
                    consultation = cursor.fetchone()
                    
                    if consultation:
                        print(f"   📋 Consulta: {consultation['symptoms_original'][:50]}...")
                        print(f"   🎯 Diagnóstico: {consultation['main_diagnosis']}")
                        print(f"   📊 Confianza: {consultation['confidence_score']}%")
                    
                    # Consultar predicciones
                    cursor.execute("SELECT * FROM predictions WHERE consultation_id = %s", (consultation_id,))
                    predictions = cursor.fetchall()
                    
                    print(f"   🔮 Predicciones: {len(predictions)} encontradas")
                    for pred in predictions:
                        print(f"      - {pred['disease_name']}: {pred['probability']}%")
                    
                    cursor.close()
                
                print("✅ ¡PRUEBA DE PRODUCCIÓN COMPLETADA EXITOSAMENTE!")
                return True
            else:
                print("❌ Error insertando predicciones")
                return False
        else:
            print("❌ Error insertando consulta")
            return False
            
    except Exception as e:
        print(f"❌ Error en prueba de producción: {e}")
        import traceback
        traceback.print_exc()
        return False

def verify_environment():
    """Verificar que el entorno esté configurado correctamente"""
    print("🔍 VERIFICANDO ENTORNO")
    print("=" * 30)
    
    # Verificar archivos críticos
    critical_files = [
        'src/database.py',
        'config/loader.py',
        '.env',
        'requirements.txt'
    ]
    
    for file_path in critical_files:
        if os.path.exists(file_path):
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - NO ENCONTRADO")
    
    # Verificar directorios
    critical_dirs = ['src', 'config', 'models']
    for dir_path in critical_dirs:
        if os.path.exists(dir_path):
            files = os.listdir(dir_path)
            print(f"   ✅ {dir_path}/ ({len(files)} archivos)")
        else:
            print(f"   ❌ {dir_path}/ - NO ENCONTRADO")
    
    # Verificar variables de entorno críticas
    print("\n🔧 Variables de entorno:")
    env_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME', 'DB_PORT']
    for var in env_vars:
        value = os.getenv(var)
        if value:
            # Mostrar solo parte del valor por seguridad
            if 'PASSWORD' in var:
                display_value = '***SET***'
            elif 'HOST' in var:
                display_value = f"{value[:20]}..." if len(value) > 20 else value
            else:
                display_value = value
            print(f"   ✅ {var}: {display_value}")
        else:
            print(f"   ❌ {var}: NO CONFIGURADA")

def main():
    """Función principal de migración"""
    
    print("🚀 MIGRACIÓN A BASE DE DATOS DE PRODUCCIÓN")
    print("=" * 60)
    
    # Verificar entorno primero
    verify_environment()
    
    # Paso 1: Verificar configuración
    if not setup_production_database():
        print("❌ Error en configuración. Verifica las variables de entorno.")
        return
    
    # Paso 2: Probar conexión
    if not test_production_connection():
        print("❌ Error de conexión. Verifica credenciales y conectividad.")
        return
    
    # Paso 3: Crear tablas
    if not create_production_tables():
        print("❌ Error creando tablas.")
        return
    
    # Paso 4: Probar funcionalidad completa
    if not test_production_insert():
        print("❌ Error en prueba de inserción.")
        return
    
    print("\n🎉 ¡MIGRACIÓN A PRODUCCIÓN COMPLETADA!")
    print("=" * 60)
    print("✅ Base de datos de producción configurada")
    print("✅ Tablas creadas correctamente")
    print("✅ Funcionalidad verificada")
    print("\n📋 Próximos pasos:")
    print("   1. python app.py (para iniciar en modo desarrollo con BD producción)")
    print("   2. Configurar FLASK_ENV=production para deployment")
    print("   3. Desplegar en Render con variables de entorno")

if __name__ == "__main__":
    main()