from flask import Blueprint, request, jsonify
from src.predictor import model_manager
import logging

api_bp = Blueprint('api', __name__)

@api_bp.route('/', methods=['GET'])
def home():
    """Endpoint de inicio"""
    return jsonify({
        "message": "SaludIA API - Sistema de Diagnóstico Médico",
        "version": "2.0",
        "available_models": model_manager.get_available_models(),
        "endpoints": {
            "predict": "POST /api/predict",
            "predict-v9": "POST /api/predict-v9", 
            "models": "GET /api/models",
            "health": "GET /api/health"
        }
    })

@api_bp.route('/predict', methods=['POST'])
def predict():
    """Predicción con texto libre"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se enviaron datos"}), 400
        
        symptoms = data.get('symptoms', '')
        model_version = data.get('model', 'v8')
        age_range = data.get('age_range')
        gender = data.get('gender')
        
        if not symptoms:
            return jsonify({"error": "Campo 'symptoms' requerido"}), 400
        
        # Realizar predicción
        result = model_manager.predict_text(symptoms, model_version, age_range, gender)
        
        if "error" in result:
            return jsonify(result), 500
        
        return jsonify({
            "success": True,
            "result": result
        })
        
    except Exception as e:
        logging.error(f"Error en /predict: {e}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/predict-v9', methods=['POST'])
def predict_v9():
    """Predicción con síntomas binarios (v9)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se enviaron datos"}), 400
        
        symptoms_binary = data.get('symptoms', [])
        
        if not symptoms_binary or not isinstance(symptoms_binary, list):
            return jsonify({"error": "Campo 'symptoms' debe ser una lista binaria"}), 400
        
        # Realizar predicción
        result = model_manager.predict_binary(symptoms_binary, 'v9')
        
        if "error" in result:
            return jsonify(result), 500
        
        return jsonify({
            "success": True,
            "result": result
        })
        
    except Exception as e:
        logging.error(f"Error en /predict-v9: {e}")
        return jsonify({"error": str(e)}), 500

@api_bp.route('/models', methods=['GET'])
def get_models():
    """Obtener información de modelos disponibles"""
    return jsonify({
        "available_models": model_manager.get_available_models(),
        "total": len(model_manager.models),
        "recommended": "v9"
    })

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Verificar estado de la API"""
    return jsonify({
        "status": "healthy",
        "models_loaded": len(model_manager.models),
        "available_models": model_manager.get_available_models()
    })