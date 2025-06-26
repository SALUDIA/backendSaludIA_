from flask import Blueprint, request, jsonify
from src.predictor import model_manager
from src.translator import translator_manager
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
            "predict-friendly": "POST /api/predict-friendly",
            "models": "GET /api/models",
            "health": "GET /api/health"
        },
        "parameters": {
            "predict-friendly": {
                "symptoms": "string (requerido) - Síntomas en español",
                "age": "int (opcional) - Edad del paciente",
                "gender": "string (opcional) - Male/Female/Masculino/Femenino",
                "model": "string (opcional) - v6/v7/v8/v8_mejorado/v9"
            }
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

@api_bp.route('/predict-friendly', methods=['POST'])
def predict_friendly():
    """Predicción amigable con traducción automática"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No se enviaron datos",
                "message": "Por favor envía los síntomas para analizar"
            }), 400
        
        symptoms_spanish = data.get('symptoms', '')
        age = data.get('age', 30)  # Edad por defecto
        gender_input = data.get('gender')  # Género del JSON
        model_version = data.get('model', 'v8')  # Modelo por defecto
        
        if not symptoms_spanish:
            return jsonify({
                "error": "Campo 'symptoms' requerido",
                "message": "Por favor describe tus síntomas"
            }), 400
        
        # 1. Extraer edad del texto si no se proporciona
        extracted_age = translator_manager.extract_age_from_text(symptoms_spanish)
        if extracted_age:
            age = extracted_age
        
        # 2. Categorizar edad
        age_range = translator_manager.categorize_age(age)
        
        # 3. Determinar género (prioridad: JSON > Detección automática)
        if gender_input:
            # Si se proporciona género en JSON, validarlo y usarlo
            gender = validate_gender(gender_input)
            gender_origin = "manual"
        else:
            # Si no se proporciona, detectar automáticamente desde síntomas
            gender = translator_manager.detect_gender(symptoms_spanish)
            gender_origin = "detectado"
        
        # 4. Traducir síntomas al inglés
        symptoms_english = translator_manager.translate_to_english(symptoms_spanish)
        
        # 5. Realizar predicción con modelo especificado
        result = model_manager.predict_text(symptoms_english, model_version, age_range, gender)
        
        if "error" in result:
            return jsonify({
                "error": result["error"],
                "message": "Error al procesar los síntomas"
            }), 500
        
        # 6. Traducir diagnóstico al español
        diagnosis_spanish = translator_manager.translate_to_spanish(result["diagnosis"])
        
        # 7. Generar recomendaciones desde BD
        recommendations = generate_recommendations(result["diagnosis"], result["confidence"])
        
        # 8. LOG EN BASE DE DATOS
        db_manager.log_prediction(
            symptoms=symptoms_spanish,
            diagnosis=result["diagnosis"],
            confidence=result["confidence"],
            model_version=model_version,
            age_detected=age,
            age_range=age_range,
            gender=gender,
            gender_origin=gender_origin,
            symptoms_processed=symptoms_english
        )
        
        return jsonify({
            "success": True,
            "result": {
                "diagnostico": diagnosis_spanish,
                "diagnostico_original": result["diagnosis"],
                "confianza": round(result["confidence"], 1),
                "edad_detectada": age,
                "rango_edad": age_range,
                "genero_usado": gender,
                "genero_origen": gender_origin,
                "modelo_usado": model_version,
                "sintomas_procesados": symptoms_english,
                "recomendaciones": recommendations,
                "timestamp": result["timestamp"],
                "logged_to_db": True  # NUEVO: Indica que se guardó en BD
            },
            "metadata": {
                "procesamiento": {
                    "traduccion_sintomas": "es → en",
                    "traduccion_diagnostico": "en → es", 
                    "categorizacion_edad": f"{age} → {age_range}",
                    "determinacion_genero": f"{'Manual: ' + str(gender_input) if gender_input else 'Auto-detectado'} → {gender}",
                    "recomendaciones_source": "database"  # NUEVO
                }
            }
        })
        
    except Exception as e:
        logging.error(f"Error en /predict-friendly: {e}")
        return jsonify({
            "error": str(e),
            "message": "Error interno del servidor"
        }), 500

def validate_gender(gender_input):
    """Validar y normalizar entrada de género"""
    if not gender_input:
        return "Unknown"
    
    gender_lower = str(gender_input).lower().strip()
    
    # Mapeo de entradas válidas
    gender_mapping = {
        # Inglés
        'male': 'Male',
        'm': 'Male',
        'man': 'Male',
        'masculine': 'Male',
        'female': 'Female',
        'f': 'Female',
        'woman': 'Female',
        'feminine': 'Female',
        'other': 'Unknown',
        'unknown': 'Unknown',
        'prefer not to say': 'Unknown',
        
        # Español
        'hombre': 'Male',
        'masculino': 'Male',
        'varón': 'Male',
        'mujer': 'Female',
        'femenino': 'Female',
        'otro': 'Unknown',
        'desconocido': 'Unknown',
        'prefiero no decir': 'Unknown'
    }
    
    return gender_mapping.get(gender_lower, 'Unknown')


from src.database import db_manager

# Reemplazar la función generate_recommendations
def generate_recommendations(diagnosis, confidence):
    """Generar recomendaciones desde la base de datos"""
    
    # 1. Obtener recomendaciones de la BD
    db_recommendations = db_manager.get_recommendations(diagnosis)
    
    # 2. Recomendaciones base por defecto
    base_recommendations = [
        "Consulta con un médico profesional para confirmar el diagnóstico",
        "Mantén un registro de tus síntomas y su evolución",
        "Sigue un estilo de vida saludable"
    ]
    
    # 3. Combinar recomendaciones
    recommendations = base_recommendations.copy()
    
    if db_recommendations:
        recommendations.extend(db_recommendations)
        print(f"✅ Obtenidas {len(db_recommendations)} recomendaciones de BD para {diagnosis}")
    else:
        print(f"⚠️ No se encontraron recomendaciones en BD para {diagnosis}, usando fallback")
        # Fallback a recomendaciones hardcodeadas si no hay en BD
        fallback_recommendations = get_fallback_recommendations(diagnosis)
        recommendations.extend(fallback_recommendations)
    
    # 4. Ajustar mensaje según confianza
    if confidence < 60:
        recommendations.insert(0, "⚠️ La confianza del diagnóstico es baja. Es especialmente importante consultar un médico.")
    elif confidence > 85:
        recommendations.insert(0, "✅ El análisis muestra alta confianza, pero siempre confirma con un profesional.")
    
    return recommendations

def get_fallback_recommendations(diagnosis):
    """Recomendaciones fallback si la BD no está disponible"""
    fallback_data = {
        "Diabetes": [
            "Controla regularmente tus niveles de glucosa",
            "Mantén una dieta balanceada baja en azúcares"
        ],
        "Hypertension": [
            "Reduce el consumo de sal en tu dieta",
            "Controla tu presión arterial regularmente"
        ],
        "Migraine": [
            "Identifica y evita los desencadenantes de dolor",
            "Mantén horarios regulares de sueño"
        ]
    }
    return fallback_data.get(diagnosis, [])

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
        "recommended": "v9",
        "descriptions": {
            "v6": "Modelo base XGBoost (rápido)",
            "v7": "Modelo ensemble (alta precisión)",
            "v8": "Modelo expandido (más enfermedades)",
            "v8_mejorado": "Modelo v8 optimizado",
            "v9": "Modelo síntomas binarios (máxima precisión)"
        }
    })

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Verificar estado de la API"""
    return jsonify({
        "status": "healthy",
        "models_loaded": len(model_manager.models),
        "available_models": model_manager.get_available_models(),
        "translator_ready": True
    })

@api_bp.route('/debug-model/<model_version>', methods=['GET'])
def debug_model(model_version):
    """Debug de información del modelo"""
    if model_version not in model_manager.models:
        return jsonify({"error": f"Modelo {model_version} no encontrado"}), 404
    
    model_data = model_manager.models[model_version]
    prep = model_data['preprocessor']
    
    debug_info = {
        "model_version": model_version,
        "type": model_data.get('type', 'unknown'),
        "preprocessors": {}
    }
    
    # Información de TF-IDF
    if 'tfidf_vectorizer' in prep:
        tfidf = prep['tfidf_vectorizer']
        debug_info['preprocessors']['tfidf'] = {
            "features_count": tfidf.get_feature_names_out().shape[0],
            "vocabulary_size": len(tfidf.vocabulary_),
            "max_features": getattr(tfidf, 'max_features', 'None')
        }
    
    # Información de encoders
    if 'age_encoder' in prep:
        debug_info['preprocessors']['age_encoder'] = {
            "classes": list(prep['age_encoder'].classes_)
        }
    
    if 'gender_encoder' in prep:
        debug_info['preprocessors']['gender_encoder'] = {
            "classes": list(prep['gender_encoder'].classes_)
        }
    
    if 'diagnosis_encoder' in prep:
        debug_info['preprocessors']['diagnosis_encoder'] = {
            "classes_count": len(prep['diagnosis_encoder'].classes_),
            "sample_classes": list(prep['diagnosis_encoder'].classes_)[:10]
        }
    
    return jsonify(debug_info)

@api_bp.route('/recommendations', methods=['GET'])
def get_all_recommendations():
    """Obtener todas las recomendaciones disponibles"""
    try:
        if not db_manager.connect():
            return jsonify({"error": "Error conectando a BD"}), 500
        
        cursor = db_manager.connection.cursor()
        query = """
            SELECT d.name_en, d.name_es, r.recommendation_text, r.category
            FROM diagnoses d 
            JOIN recommendations r ON d.id = r.diagnosis_id
            WHERE r.is_active = TRUE
            ORDER BY d.name_en, r.priority
        """
        cursor.execute(query)
        results = cursor.fetchall()
        cursor.close()
        db_manager.disconnect()
        
        # Organizar por diagnóstico
        recommendations_by_diagnosis = {}
        for diagnosis_en, diagnosis_es, rec_text, category in results:
            if diagnosis_en not in recommendations_by_diagnosis:
                recommendations_by_diagnosis[diagnosis_en] = {
                    "diagnosis_english": diagnosis_en,
                    "diagnosis_spanish": diagnosis_es,
                    "recommendations": []
                }
            recommendations_by_diagnosis[diagnosis_en]["recommendations"].append({
                "text": rec_text,
                "category": category
            })
        
        return jsonify({
            "success": True,
            "data": recommendations_by_diagnosis,
            "total_diagnoses": len(recommendations_by_diagnosis)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Agregar a api.py si quieres un endpoint de verificación
@api_bp.route('/verify-recommendations', methods=['GET'])
def verify_recommendations():
    """Verificar estado de recomendaciones en BD"""
    try:
        if not db_manager.connect():
            return jsonify({"error": "No se pudo conectar a BD"}), 500
        
        cursor = db_manager.connection.cursor()
        
        # Contar por enfermedad
        cursor.execute("""
            SELECT d.name_en, d.name_es, COUNT(r.id) as rec_count
            FROM diagnoses d 
            LEFT JOIN recommendations r ON d.id = r.diagnosis_id AND r.is_active = TRUE
            GROUP BY d.id, d.name_en, d.name_es
            ORDER BY rec_count DESC, d.name_en
        """)
        
        results = cursor.fetchall()
        cursor.close()
        db_manager.disconnect()
        
        return jsonify({
            "success": True,
            "total_diseases": len(results),
            "diseases": [
                {
                    "name_en": row[0],
                    "name_es": row[1],
                    "recommendations_count": row[2]
                }
                for row in results
            ]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
