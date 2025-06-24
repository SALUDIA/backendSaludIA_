from flask import Flask, request, jsonify
from flask_cors import CORS
from config.loader import get_config_instance, get_db_config
import os
import logging

# Crear aplicación Flask
app = Flask(__name__)

# Configurar CORS
CORS(app, resources={
    r"/*": {
        "origins": ["*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configurar logging para producción
if os.getenv('FLASK_ENV') == 'production':
    logging.basicConfig(level=logging.INFO)
    app.logger.setLevel(logging.INFO)

# Importar rutas después de crear app
from src.predictor import predictor_bp
from src.database import database_bp

# Registrar blueprints
app.register_blueprint(predictor_bp)
app.register_blueprint(database_bp)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        db_config = get_db_config()
        db_host = db_config.get('host', 'unknown')
        
        return jsonify({
            'status': 'healthy',
            'message': 'SaludIA API is running',
            'database': 'Aiven MySQL' if 'aivencloud.com' in db_host else 'Local MySQL',
            'environment': os.getenv('FLASK_ENV', 'development'),
            'version': '1.0.0'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        'message': 'SaludIA Backend API',
        'version': '1.0.0',
        'endpoints': {
            'health': '/health',
            'predict': '/predict-friendly',
            'predict_v9': '/predict-v9'
        }
    })