from src.api import app
from config.loader import get_config_instance, get_db_config
import os

# 🔧 CONFIGURACIÓN PARA DESARROLLO LOCAL CON BD EN LÍNEA
if __name__ == '__main__':
    try:
        # ⚡ CONFIGURACIÓN LOCAL CON AIVEN
        print("🚀 SaludIA Backend - Iniciando en LOCAL...")
        print("="*60)
        
        # Forzar uso de base de datos en línea (Aiven)
        os.environ['FORCE_AIVEN'] = 'true'
        os.environ['FLASK_ENV'] = 'development'  # ← Para debugging local
        
        # Puerto y host para desarrollo local
        port = int(os.environ.get('PORT', 5000))
        host = '127.0.0.1'  # ← Solo localhost
        
        print(f"🔧 Entorno: development (local)")
        print(f"🌐 Puerto: {port}")
        print(f"🏠 Host: {host}")
        
        # Verificar configuración de BD
        try:
            db_config = get_db_config()
            db_host = db_config.get('host', 'unknown')
            
            if 'aivencloud.com' in db_host:
                print("✅ Base de datos: Aiven MySQL (EN LÍNEA)")
                print(f"   🌐 Host: {db_host}")
                print(f"   📊 BD: {db_config.get('database')}")
                print(f"   🔒 SSL: Habilitado")
            else:
                print(f"⚠️ Base de datos: {db_host}")
                print("❌ No se está usando Aiven como esperado")
                
        except Exception as e:
            print(f"⚠️ Error verificando BD: {e}")
        
        # Verificar modelos cargados
        try:
            from src.predictor import predictor, predictor_v9
            
            print("\n🤖 MODELOS ML:")
            if predictor:
                print("   ✅ Modelo v8: Cargado")
            else:
                print("   ❌ Modelo v8: No disponible")
                
            if predictor_v9:
                print("   ✅ Modelo v9: Cargado")
            else:
                print("   ❌ Modelo v9: No disponible")
                
        except Exception as e:
            print(f"   ⚠️ Error verificando modelos: {e}")
        
        print("\n📋 API Endpoints disponibles:")
        print("   POST /predict-friendly - Diagnóstico amigable")
        print("   POST /predict - Diagnóstico técnico")  
        print("   POST /predict-v9 - Síntomas binarios")
        print("   GET /health - Estado del sistema")
        print("   GET /symptoms-v9 - Lista síntomas v9")
        
        print("\n🔗 URLs de prueba:")
        print(f"   http://{host}:{port}/health")
        print(f"   http://{host}:{port}/")
        
        print("="*60)
        print("🎯 LISTO PARA DESARROLLAR LOCALMENTE")
        print("💡 Presiona Ctrl+C para detener")
        print("="*60)
        
        # 🚀 INICIAR SERVIDOR LOCAL CON BD EN LÍNEA
        app.run(
            debug=True,      # ← Debug habilitado para desarrollo
            host=host,       # ← Solo localhost  
            port=port,
            threaded=True,
            use_reloader=True  # ← Auto-reload en cambios
        )
        
    except KeyboardInterrupt:
        print("\n👋 Servidor detenido por el usuario")
        
    except Exception as e:
        print(f"\n❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()
        exit(1)