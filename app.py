import os
import logging
from flask import Flask
from flask_cors import CORS
import sys

# Configurar logging optimizado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

def create_app():
    """Factory optimizada - SOLO MODELO V11"""
    app = Flask(__name__)
    
    # Configuración mínima
    app.config['DEBUG'] = False
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'saludia-v11-secret')
    
    # CORS optimizado
    CORS(app, origins=["*"])
    
    # CARGAR SOLO MODELO V11
    print("🚀 Iniciando aplicación optimizada - SOLO MODELO V11...")
    
    try:
        # Verificar que el modelo v11 esté disponible
        model_path = 'models/v11_components/'
        required_files = [
            'modelo_xgb.pkl',
            'tfidf_vectorizer.pkl',
            'metadata.pkl',
            'preprocesador_data.pkl'
        ]
        
        missing_files = []
        for file in required_files:
            if not os.path.exists(os.path.join(model_path, file)):
                missing_files.append(file)
        
        if missing_files:
            raise Exception(f"Archivos faltantes del modelo v11: {missing_files}")
        
        # Cargar modelo v11
        from src.model_loader_v11 import cargar_modelo_v11
        modelo_v11 = cargar_modelo_v11()
        
        if modelo_v11.modelo_xgb is not None:
            print("✅ Modelo v11 cargado exitosamente - APLICACIÓN LISTA")
        else:
            raise Exception("Modelo v11 no se cargó correctamente")
            
    except Exception as e:
        print(f"❌ ERROR CRÍTICO - Modelo v11 falló: {e}")
        print("🚨 La aplicación solo funciona con modelo v11")
        sys.exit(1)  # Terminar si no hay modelo v11
    
    # Registrar solo el API v11
    from src.api_v11 import api_v11_bp
    app.register_blueprint(api_v11_bp, url_prefix='/api')
    
    print("✅ Aplicación optimizada lista - SOLO MODELO V11")
    return app

# Crear aplicación
app = create_app()

@app.route('/')
def home():
    """Ruta principal optimizada"""
    return {
        "message": "SaludIA Backend API - MODELO V11 ÚNICAMENTE",
        "version": "3.0 - Optimizado",
        "modelo": "v11 (NLP Semántico Avanzado)",
        "status": "running",
        "features": [
            "Sentence-BERT + TF-IDF",
            "Diccionario médico bilingüe",
            "Detección automática de edad/género",
            "Top 3 diagnósticos",
            "Embeddings semánticos 384D"
        ],
        "endpoints": {
            "predict": "POST /api/predict-v11",
            "health": "GET /api/health",
            "info": "GET /api/model-info"
        },
        "port": os.environ.get('PORT', 10000)
    }

@app.route('/health')
def health():
    """Health check optimizado"""
    try:
        from src.model_loader_v11 import modelo_v11_global
        modelo_status = (modelo_v11_global is not None and 
                        hasattr(modelo_v11_global, 'modelo_xgb') and 
                        modelo_v11_global.modelo_xgb is not None)
    except:
        modelo_status = False
    
    return {
        "status": "healthy" if modelo_status else "error",
        "service": "saludia-v11-only",
        "modelo_v11": "loaded" if modelo_status else "failed",
        "optimized": True,
        "size": "minimal",
        "port": os.environ.get('PORT', 10000)
    }

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 10000))
    print(f"🚀 Servidor optimizado v11 en 0.0.0.0:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)