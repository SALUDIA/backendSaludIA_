import os
import logging
from flask import Flask
from flask_cors import CORS
import sys

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def create_app():
    """Factory optimizada - SOLO MODELO V11"""
    app = Flask(__name__)
    
    app.config['DEBUG'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'saludia-v11-secret')
    
    CORS(app, origins=["*"])
    
    print("🚀 Iniciando aplicación optimizada - SOLO MODELO V11...")
    
    try:
        # Intentar cargar modelo v11
        from src.model_loader_v11 import cargar_modelo_v11
        modelo_v11 = cargar_modelo_v11()
        
        if hasattr(modelo_v11, 'modelo_xgb') and modelo_v11.modelo_xgb is not None:
            print("✅ Modelo v11 cargado exitosamente - APLICACIÓN LISTA")
        else:
            print("⚠️ Modelo v11 cargado pero verificar estado")
            
    except Exception as e:
        print(f"❌ ERROR CRÍTICO - Modelo v11 falló: {e}")
        print("🚨 Continuando sin modelo v11 (modo degradado)")
    
    # Registrar API
    try:
        from src.api import api_bp
        app.register_blueprint(api_bp, url_prefix='/api')
        print("✅ API registrada")
    except Exception as e:
        print(f"⚠️ Error registrando API: {e}")
    
    print("✅ Aplicación lista")
    return app

app = create_app()

@app.route('/')
def home():
    """Ruta principal - IMPORTANTE para Render"""
    port = os.environ.get('PORT', '10000')
    return {
        "message": "🏥 SaludIA Backend API - MODELO V11",
        "version": "3.0 - Optimizado para Render",
        "status": "✅ RUNNING",
        "port": port,  # ← CORREGIDO: removido | 10000
        "render_ready": True,
        "endpoints": {
            "predict_v11": "POST /api/predict-v11",
            "health": "GET /health",
            "api_info": "GET /api/"
        }
    }

@app.route('/health')
def health():
    """Health check para Render"""
    port = os.environ.get('PORT', '10000')
    
    try:
        from src.model_loader_v11 import modelo_v11_global
        modelo_status = (hasattr(modelo_v11_global, 'modelo_xgb') and 
                        modelo_v11_global.modelo_xgb is not None)
    except:
        modelo_status = False
    
    return {
        "status": "healthy" if modelo_status else "degraded",
        "service": "saludia-v11",
        "modelo_v11": "✅ loaded" if modelo_status else "⚠️ checking",
        "port": port,
        "render_deployment": "active"
    }

@app.route('/test-db')
def test_db():
    """Test de conexión a base de datos"""
    try:
        from src.database import db_manager
        
        # Mostrar configuración (sin password)
        config_info = {
            "host": os.environ.get('DB_HOST', 'NO DEFINIDO'),
            "user": os.environ.get('DB_USER', 'NO DEFINIDO'),
            "database": os.environ.get('DB_NAME', 'NO DEFINIDO'),
            "port": os.environ.get('DB_PORT', 'NO DEFINIDO'),
            "flask_env": os.environ.get('FLASK_ENV', 'NO DEFINIDO')
        }
        
        # Probar conexión
        connection_result = db_manager.test_connection()
        
        return {
            "database_config": config_info,
            "connection_test": connection_result,
            "status": "connected" if connection_result.get("status") == "success" else "disconnected"
        }
        
    except Exception as e:
        return {
            "error": str(e),
            "status": "error",
            "message": "Error probando conexión BD"
        }, 500

if __name__ == "__main__":
    # ¡CRÍTICO! Puerto dinámico de Render
    port = int(os.environ.get('PORT', 10000))
    host = '0.0.0.0'
    
    print(f"🚀 Servidor SaludIA iniciando en {host}:{port}")
    print(f"🌐 Puerto Render detectado: {port}")
    print(f"📡 Escuchando en todas las interfaces: {host}")
    
    # ASEGURAR QUE FLASK ESCUCHE CORRECTAMENTE
    app.run(
        host=host, 
        port=port, 
        debug=False,
        threaded=True,
        use_reloader=False
    )