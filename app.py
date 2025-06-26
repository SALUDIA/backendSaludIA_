from flask import Flask
from flask_cors import CORS
from src.api import api_bp
from src.config import Config
import logging

# Configurar logging básico
logging.basicConfig(level=logging.INFO)

def create_app():
    """Factory para crear la aplicación Flask"""
    app = Flask(__name__)
    
    # Configuración
    app.config['DEBUG'] = Config.DEBUG
    
    # CORS
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
        "version": "2.0 Simplificado",
        "status": "running"
    }

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)