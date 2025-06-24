import os
from config.loader import get_db_config

def check_database_config():
    """Verificar configuración actual de base de datos"""
    print("🔍 VERIFICANDO CONFIGURACIÓN DE BASE DE DATOS")
    print("=" * 60)
    
    # Variables de entorno clave
    env = os.getenv('FLASK_ENV', 'development')  
    force_aiven = os.getenv('FORCE_AIVEN', 'false').lower() == 'true'
    
    print(f"🔧 Entorno: {env}")
    print(f"🔧 Forzar Aiven: {force_aiven}")
    
    # Obtener configuración de BD
    db_config = get_db_config()
    
    print(f"\n📊 CONFIGURACIÓN DE BASE DE DATOS:")
    print(f"   Host: {db_config.get('host', 'No configurado')}")
    print(f"   Puerto: {db_config.get('port', 'No configurado')}")
    print(f"   Usuario: {db_config.get('user', 'No configurado')}")
    print(f"   Base de datos: {db_config.get('database', 'No configurado')}")
    print(f"   SSL: {'Habilitado' if not db_config.get('ssl_disabled', True) else 'Deshabilitado'}")
    
    # Determinar tipo de BD
    host = db_config.get('host', '')
    if 'aivencloud.com' in host or env == 'production':
        print(f"\n✅ USANDO: Base de datos AIVEN (Producción)")
        print(f"🌐 Conexión: Remota con SSL")
    elif host == 'localhost':
        print(f"\n⚠️ USANDO: Base de datos LOCAL (Desarrollo)")
        print(f"🏠 Conexión: Local sin SSL")
    else:
        print(f"\n❓ USANDO: Base de datos DESCONOCIDA")
    
    # Verificar variables críticas
    print(f"\n🔍 VARIABLES DE ENTORNO CRÍTICAS:")
    critical_vars = ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']
    
    for var in critical_vars:
        value = os.getenv(var)
        if value:
            display_value = value if var != 'DB_PASSWORD' else '*' * 8
            print(f"   ✅ {var}: {display_value}")
        else:
            print(f"   ❌ {var}: No configurado")
    
    print(f"\n📋 PARA FORZAR PRODUCCIÓN:")
    print(f"   export FLASK_ENV=production")
    print(f"   # O alternativamente:")
    print(f"   export FORCE_AIVEN=true")

if __name__ == '__main__':
    check_database_config()