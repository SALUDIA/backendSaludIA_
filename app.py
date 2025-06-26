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
    
    return app

# Crear aplicación
app = create_app()

@app.route('/')
def home():
    """Ruta principal"""
    return {
        "message": "SaludIA Backend API",
        "version": "2.0 Producción",
        "status": "running",
        "environment": os.getenv('FLASK_ENV', 'development')
    }

@app.route('/health')
def health():
    """Health check para Render"""
    return {
        "status": "healthy",
        "service": "saludia-backend",
        "database": "connected" if Config.FORCE_AIVEN else "local"
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=Config.DEBUG)