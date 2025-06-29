from flask import Blueprint, request, jsonify
import logging
import pandas as pd

api_bp = Blueprint('api', __name__)

# IMPORTAR MODELO V11
try:
    from src.model_loader_v11 import modelo_v11_global
    MODELO_V11_DISPONIBLE = True
    print("✅ Modelo v11 importado en api.py")
except Exception as e:
    print(f"⚠️ Modelo v11 no disponible en api.py: {e}")
    MODELO_V11_DISPONIBLE = False

@api_bp.route('/', methods=['GET'])
def home():
    """Endpoint de inicio"""
    return jsonify({
        "message": "SaludIA API - Sistema de Diagnóstico Médico",
        "version": "3.0 - Optimizado para Render",
        "available_models": ["v11_backup"] if MODELO_V11_DISPONIBLE else [],
        "endpoints": {
            "predict-v11": "POST /api/predict-v11",
            "health": "GET /api/health"
        },
        "status": "✅ RUNNING"
    })

@api_bp.route('/predict-v11', methods=['POST'])
def predict_v11():
    """Predicción v11 optimizada para memoria limitada"""
    try:
        if not MODELO_V11_DISPONIBLE:
            return jsonify({
                "error": "Modelo v11 no disponible",
                "message": "El modelo no está cargado"
            }), 503
        
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se enviaron datos"}), 400
        
        symptoms = data.get('symptoms', '')
        age = data.get('age')
        gender = data.get('gender')
        
        if not symptoms:
            return jsonify({"error": "Campo 'symptoms' es requerido"}), 400
        
        # Usar modelo v11 global
        if not modelo_v11_global.modelo_cargado:
            return jsonify({"error": "Modelo v11 no está cargado correctamente"}), 500
        
        # Realizar predicción
        result = modelo_v11_global.predict_symptoms(symptoms, age, gender)
        
        if "error" in result:
            return jsonify({
                "error": result["error"],
                "message": "Error en predicción"
            }), 500
        
        return jsonify({
            "success": True,
            "result": result,
            "metadata": {
                "version": "v11_backup",
                "optimizado_para": "Render Free 512MB",
                "timestamp": pd.Timestamp.now().isoformat()
            }
        })
        
    except Exception as e:
        logging.error(f"Error en /predict-v11: {e}")
        return jsonify({
            "error": str(e),
            "message": "Error interno del servidor"
        }), 500

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Verificar estado de la API"""
    modelo_v11_status = False
    if MODELO_V11_DISPONIBLE:
        try:
            modelo_v11_status = modelo_v11_global.modelo_cargado
        except:
            pass
    
    return jsonify({
        "status": "healthy",
        "modelo_v11": "loaded" if modelo_v11_status else "unavailable",
        "modelo_disponible": MODELO_V11_DISPONIBLE,
        "memoria_optimizada": True
    })

@api_bp.route('/test-model', methods=['GET'])
def test_model():
    """Endpoint para probar el modelo"""
    try:
        if not MODELO_V11_DISPONIBLE or not modelo_v11_global.modelo_cargado:
            return jsonify({
                "status": "error",
                "message": "Modelo no disponible"
            })
        
        # Prueba básica
        test_result = modelo_v11_global.predict_symptoms("dolor de cabeza", 30, "Male")
        
        return jsonify({
            "status": "success",
            "test_result": test_result,
            "modelo_funcionando": True
        })
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500