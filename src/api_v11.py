from flask import Blueprint, request, jsonify
from src.model_loader_v11 import cargar_modelo_v11, predecir_v11
from src.translator import translator_manager
import logging
import pandas as pd

api_v11_bp = Blueprint('api_v11', __name__)

@api_v11_bp.route('/predict-v11', methods=['POST'])
def predict_v11():
    """Predicción SOLO con modelo v11"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No se enviaron datos",
                "message": "Por favor envía los síntomas para analizar"
            }), 400
        
        # Obtener parámetros
        symptoms = data.get('symptoms', '')
        age = data.get('age', 30)
        gender_input = data.get('gender')
        
        if not symptoms or len(symptoms.strip()) < 3:
            return jsonify({
                "error": "Síntomas insuficientes",
                "message": "Por favor describe tus síntomas con más detalle"
            }), 400
        
        # Procesar edad y género
        try:
            extracted_age = translator_manager.extract_age_from_text(symptoms)
            if extracted_age:
                age = extracted_age
            age_range = translator_manager.categorize_age(age)
        except:
            age_range = "25-34"
        
        if gender_input:
            gender = validate_gender(gender_input)
        else:
            try:
                gender = translator_manager.detect_gender(symptoms)
            except:
                gender = "Unknown"
        
        # Realizar predicción con modelo v11
        result = predecir_v11(symptoms, age_range, gender)
        
        if "error" in result:
            return jsonify({
                "error": result["error"],
                "message": "Error procesando con modelo v11"
            }), 500
        
        # Traducir diagnóstico al español
        try:
            diagnosis_spanish = translator_manager.translate_to_spanish(result["diagnostico_principal"])
        except:
            diagnosis_spanish = result["diagnostico_principal"]
        
        return jsonify({
            "success": True,
            "result": {
                "diagnostico": diagnosis_spanish,
                "diagnostico_original": result["diagnostico_principal"],
                "confianza": round(result["confianza"] * 100, 1),
                "top_diagnosticos": result.get("top_diagnosticos", []),
                "edad_detectada": age,
                "genero_usado": gender,
                "modelo_usado": "v11",
                "idioma_detectado": result.get("idioma_detectado", "spanish"),
                "embeddings_generados": result.get("procesamiento", {}).get("embeddings_generados", True),
                "timestamp": pd.Timestamp.now().isoformat()
            }
        })
        
    except Exception as e:
        logging.error(f"Error en /predict-v11: {e}")
        return jsonify({
            "error": str(e),
            "message": "Error interno del servidor"
        }), 500

@api_v11_bp.route('/model-info', methods=['GET'])
def model_info():
    """Información del modelo v11"""
    try:
        modelo = cargar_modelo_v11()
        info = modelo.get_model_info()
        
        return jsonify({
            "success": True,
            "model_info": info,
            "capabilities": {
                "nlp_avanzado": "Sentence-BERT + TF-IDF",
                "idiomas": ["Español", "Inglés"],
                "embeddings": "384 dimensiones semánticas",
                "top_predictions": 3
            }
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@api_v11_bp.route('/health', methods=['GET'])
def health_check():
    """Health check del modelo v11"""
    try:
        modelo = cargar_modelo_v11()
        status = modelo.modelo_xgb is not None
        
        return jsonify({
            "status": "healthy" if status else "error",
            "modelo_v11": "loaded" if status else "failed",
            "endpoint": "/api/predict-v11"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

def validate_gender(gender_input):
    """Validar género"""
    if not gender_input:
        return "Unknown"
    
    gender_mapping = {
        'male': 'Male', 'm': 'Male', 'hombre': 'Male', 'masculino': 'Male',
        'female': 'Female', 'f': 'Female', 'mujer': 'Female', 'femenino': 'Female'
    }
    
    return gender_mapping.get(str(gender_input).lower().strip(), 'Unknown')