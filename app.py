from flask import Flask
from flask_cors import CORS
from src.api import api_bp
from src.config import Config
import logging
import os

# Configurar logging para producción
if os.getenv('FLASK_ENV') == 'production':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(message)s'
    )
else:
    logging.basicConfig(level=logging.INFO)

def create_app():
    """Factory para crear la aplicación Flask"""
    app = Flask(__name__)
    
    # Configuración
    app.config['DEBUG'] = Config.DEBUG
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    
    # CORS más específico para producción
    if os.getenv('FLASK_ENV') == 'production':
        CORS(app, origins=["*"])  # Puedes ser más específico aquí
    else:
        CORS(app)
    
    # Registrar blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # NUEVO: Cargar modelo v11 al inicio
    print("🚀 Iniciando carga de modelos...")
    try:
        from src.model_loader_v11 import cargar_modelo_v11
        modelo_v11 = cargar_modelo_v11()
        if modelo_v11.modelo_xgb is not None:
            print("✅ Modelo v11 cargado exitosamente en la aplicación")
        else:
            print("⚠️ Modelo v11 no se pudo cargar completamente")
    except Exception as e:
        print(f"❌ Error cargando modelo v11: {e}")
    
    print("✅ Aplicación Flask inicializada con soporte para modelo v11")
    
    return app

# Crear aplicación
app = create_app()

@app.route('/')
def home():
    """Ruta principal"""
    return {
        "message": "SaludIA Backend API",
        "version": "2.1 Producción con Modelo v11",  # Actualizar versión
        "status": "running",
        "environment": os.getenv('FLASK_ENV', 'development'),
        "new_features": "🚀 Modelo v11 con NLP semántico avanzado disponible en /api/predict-v11"
    }

@app.route('/health')
def health():
    """Health check para Render"""
    try:
        from src.model_loader_v11 import modelo_v11_global
        modelo_v11_status = modelo_v11_global is not None and modelo_v11_global.modelo_xgb is not None
    except:
        modelo_v11_status = False
    
    return {
        "status": "healthy",
        "service": "saludia-backend",
        "database": "connected" if Config.FORCE_AIVEN else "local",
        "modelo_v11": "loaded" if modelo_v11_status else "unavailable",
        "python_version": "3.10.2",
        "port": os.environ.get('PORT', 10000)
    }

# Para Render - importante
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    host = '0.0.0.0'  # Forzar para Render
    
    print(f"🚀 Iniciando servidor en {host}:{port}")
    
    app.run(
        host=host,
        port=port,
        debug=os.environ.get('DEBUG_MODE', 'false').lower() == 'true',
        threaded=True
    )