import os
import sys


# Agregar Backend al path
backend_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_path)

from config.loader import get_config_instance, get_db_config, get_cors_config, validate_environment

def test_full_configuration():
    """Probar configuración completa"""
    print("🧪 PROBANDO CONFIGURACIÓN COMPLETA")
    print("=" * 60)
    
    # Test 1: Validar variables de entorno
    print("🔍 1. Validando variables de entorno...")
    try:
        env_valid = validate_environment()
        if env_valid:
            print("✅ Variables de entorno válidas")
        else:
            print("⚠️ Faltan algunas variables de entorno")
    except Exception as e:
        print(f"❌ Error validando entorno: {e}")
    
    # Test 2: Configuración general
    print("\n⚙️ 2. Cargando configuración...")
    try:
        config = get_config_instance()
        print(f"✅ Configuración: {config.__class__.__name__}")
    except Exception as e:
        print(f"❌ Error cargando configuración: {e}")
        return
    
    # Test 3: Configuración de BD
    print("\n🗄️ 3. Configuración de base de datos...")
    try:
        db_config = get_db_config()
        print(f"✅ BD Host: {db_config.get('host', 'No configurado')}")
        print(f"✅ BD Port: {db_config.get('port', 'No configurado')}")
        print(f"✅ BD Database: {db_config.get('database', 'No configurado')}")
        print(f"✅ SSL: {'Habilitado' if not db_config.get('ssl_disabled', True) else 'Deshabilitado'}")
    except Exception as e:
        print(f"❌ Error configuración BD: {e}")
    
    # Test 4: Configuración CORS
    print("\n🌐 4. Configuración CORS...")
    try:
        cors_config = get_cors_config()
        print(f"✅ Origins: {cors_config.get('origins', 'No configurado')}")
        print(f"✅ Methods: {cors_config.get('methods', 'No configurado')}")
        print(f"✅ Headers: {cors_config.get('allow_headers', 'No configurado')}")
        print(f"✅ Credentials: {cors_config.get('supports_credentials', 'No configurado')}")
    except Exception as e:
        print(f"❌ Error configuración CORS: {e}")
    
    # Test 5: Variables específicas
    print("\n🔧 5. Variables específicas...")
    specific_vars = [
        'FLASK_ENV',
        'MODEL_VERSION',
        'TRANSLATOR_TIMEOUT',
        'API_RATE_LIMIT',
        'LOG_LEVEL',
        'ENABLE_TRANSLATION',
        'ENABLE_V9_MODEL',
        'DB_HOST',
        'SECRET_KEY'
    ]
    
    for var in specific_vars:
        value = os.getenv(var, 'NO CONFIGURADA')
        # Ocultar valores sensibles
        if 'SECRET' in var or 'PASSWORD' in var:
            value = '***CONFIGURADA***' if value != 'NO CONFIGURADA' else 'NO CONFIGURADA'
        elif 'DB_HOST' in var and value != 'NO CONFIGURADA':
            value = f"{value[:20]}..." if len(value) > 20 else value
        print(f"   {var}: {value}")
    
    # Test 6: Probar conexión a BD
    print("\n🔗 6. Probando conexión a base de datos...")
    try:
        from src.database import db_manager
        connection_success = db_manager.test_connection()
        if connection_success:
            print("✅ Conexión a BD exitosa")
        else:
            print("❌ Error de conexión a BD")
    except Exception as e:
        print(f"❌ Error probando BD: {e}")
    
    print(f"\n🎉 ¡PRUEBA DE CONFIGURACIÓN COMPLETADA!")

if __name__ == "__main__":
    test_full_configuration()