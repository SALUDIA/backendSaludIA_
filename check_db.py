"""
check_db.py - Script simple para verificar BD (en Backend/)
"""
import os
from dotenv import load_dotenv

load_dotenv()

def check_current_database():
    """Verificar qué base de datos estamos usando"""
    
    print("🔍 VERIFICACIÓN RÁPIDA DE BASE DE DATOS")
    print("=" * 50)
    
    # Mostrar variables de entorno
    print("📋 Variables de entorno:")
    db_vars = {
        'FLASK_ENV': os.getenv('FLASK_ENV', 'development'),
        'FORCE_AIVEN': os.getenv('FORCE_AIVEN', 'false'),
        'DB_HOST': os.getenv('DB_HOST', 'No configurado'),
        'DB_PORT': os.getenv('DB_PORT', 'No configurado'),
        'DB_USER': os.getenv('DB_USER', 'No configurado'),
        'DB_NAME': os.getenv('DB_NAME', 'No configurado'),
        'LOCAL_DB_HOST': os.getenv('LOCAL_DB_HOST', 'No configurado')
    }
    
    for var, value in db_vars.items():
        if 'PASSWORD' in var:
            display = '***SET***' if value != 'No configurado' else 'No configurado'
        else:
            display = value
        print(f"   {var}: {display}")
    
    # Determinar qué BD se usará
    print(f"\n🎯 LÓGICA DE SELECCIÓN DE BD:")
    
    env = os.getenv('FLASK_ENV', 'development')
    force_aiven = os.getenv('FORCE_AIVEN', 'false').lower() == 'true'
    has_local = bool(os.getenv('LOCAL_DB_HOST'))
    has_aiven = bool(os.getenv('DB_HOST'))
    
    print(f"   Entorno: {env}")
    print(f"   Forzar Aiven: {force_aiven}")
    print(f"   Tiene config local: {has_local}")
    print(f"   Tiene config Aiven: {has_aiven}")
    
    # Aplicar lógica de config/loader.py
    if env == 'production' or force_aiven:
        print(f"\n✅ USARÁ: AIVEN (Producción)")
        print(f"   Razón: {'Entorno producción' if env == 'production' else 'FORCE_AIVEN=true'}")
        expected_host = os.getenv('DB_HOST')
    elif has_local and not force_aiven:
        print(f"\n⚠️ USARÁ: LOCAL (Desarrollo)")
        print(f"   Razón: Tiene configuración local y no fuerza Aiven")
        expected_host = os.getenv('LOCAL_DB_HOST')
    elif has_aiven:
        print(f"\n🌐 USARÁ: AIVEN (Fallback)")
        print(f"   Razón: No tiene local, usa Aiven como fallback")
        expected_host = os.getenv('DB_HOST')
    else:
        print(f"\n❌ PROBLEMA: No hay configuración válida")
        return
    
    print(f"   Host esperado: {expected_host}")
    
    # Probar conexión real
    print(f"\n🔗 PROBANDO CONEXIÓN REAL...")
    try:
        from config.loader import get_db_config
        from src.database import db_manager
        
        # Obtener config real
        actual_config = get_db_config()
        actual_host = actual_config.get('host')
        
        print(f"   Config real obtenida:")
        print(f"     Host: {actual_host}")
        print(f"     Puerto: {actual_config.get('port')}")
        print(f"     BD: {actual_config.get('database')}")
        print(f"     SSL: {'Habilitado' if not actual_config.get('ssl_disabled', True) else 'Deshabilitado'}")
        
        # Verificar si coincide
        if actual_host == expected_host:
            print(f"   ✅ Configuración coincide con lo esperado")
        else:
            print(f"   ⚠️ Configuración diferente a lo esperado")
        
        # Probar conexión
        success = db_manager.test_connection()
        
        if success:
            print(f"   ✅ CONEXIÓN EXITOSA")
            
            # Identificar tipo de BD por host
            if 'aivencloud.com' in actual_host:
                print(f"   🌐 CONFIRMADO: Usando AIVEN MySQL (Producción)")
            elif actual_host in ['localhost', '127.0.0.1']:
                print(f"   🏠 CONFIRMADO: Usando MySQL LOCAL (Desarrollo)")
            else:
                print(f"   ❓ Usando BD desconocida: {actual_host}")
                
        else:
            print(f"   ❌ ERROR DE CONEXIÓN")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n💡 PARA CAMBIAR A PRODUCCIÓN:")
    print(f"   1. export FLASK_ENV=production")
    print(f"   2. export FORCE_AIVEN=true") 
    print(f"   3. Agregar FORCE_AIVEN=true al .env")

if __name__ == '__main__':
    check_current_database()