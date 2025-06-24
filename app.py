from src.api import app
from config.loader import get_config_instance, get_db_config
import os
import logging

# Configurar logging para producción
if os.getenv('FLASK_ENV') == 'production':
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)

if __name__ == '__main__':
    try:
        # 🚀 CONFIGURACIÓN OPTIMIZADA PARA RENDER
        port = int(os.environ.get('PORT', 5000))
        environment = os.environ.get('FLASK_ENV', 'production')
        is_production = environment == 'production'
        
        print("🚀 SaludIA Backend - Iniciando en Render...")
        print(f"🔧 Entorno: {environment}")
        print(f"🌐 Puerto: {port}")
        
        # Verificar configuración de BD
        try:
            db_config = get_db_config()
            db_host = db_config.get('host', 'unknown')
            if 'aivencloud.com' in db_host:
                print("✅ Base de datos: Aiven MySQL conectada")
            else:
                print(f"⚠️ Base de datos: {db_host}")
        except Exception as e:
            print(f"⚠️ Error verificando BD: {e}")
        
        print("📋 API Endpoints disponibles:")
        print("   POST /predict-friendly - Diagnóstico amigable")
        print("   POST /predict - Diagnóstico técnico")
        print("   POST /predict-v9 - Síntomas binarios")
        print("   GET /health - Estado del sistema")
        print("="*50)
        
        # Configuración específica para Render
        app.run(
            debug=False,  # ← Siempre False en producción
            host='0.0.0.0',  # ← Permite conexiones externas
            port=port,
            threaded=True,
            use_reloader=False  # ← Evita problemas en Render
        )
        
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()
        exit(1)