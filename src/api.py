from flask import Blueprint, request, jsonify
from src.predictor import model_manager
from src.translator import translator_manager
import logging
import pandas as pd

api_bp = Blueprint('api', __name__)

# IMPORTAR MODELO V11
try:
    from src.predictor import model_manager_v11
    MODELO_V11_DISPONIBLE = True
    print("✅ Modelo v11 importado en api.py")
except Exception as e:
    print(f"⚠️ Modelo v11 no disponible en api.py: {e}")
    MODELO_V11_DISPONIBLE = False

@api_bp.route('/', methods=['GET'])
def home():
    """Endpoint de inicio (ACTUALIZADO con v11)"""
    modelos_disponibles = model_manager.get_available_models()
    if MODELO_V11_DISPONIBLE:
        try:
            modelos_todos = model_manager_v11.get_available_models()
            modelos_disponibles = modelos_todos
        except:
            pass
    
    return jsonify({
        "message": "SaludIA API - Sistema de Diagnóstico Médico",
        "version": "2.1",
        "available_models": modelos_disponibles,
        "featured": "v11 - NLP Semántico Avanzado" if "v11" in modelos_disponibles else "v9",
        "endpoints": {
            "predict-v11": "POST /api/predict-v11 (🚀 NUEVO - NLP Avanzado)",
            "predict": "POST /api/predict",
            "predict-v9": "POST /api/predict-v9", 
            "predict-friendly": "POST /api/predict-friendly",
            "models": "GET /api/models",
            "health": "GET /api/health"
        },
        "new_features": {
            "modelo_v11": {
                "nlp_semantico": "Sentence-BERT + TF-IDF",
                "diccionario_medico": "Bilingüe ES/EN",
                "embeddings": "384 dimensiones semánticas",
                "top_diagnosticos": "3 predicciones principales"
            }
        }
    })

# ========== NUEVO ENDPOINT V11 ==========
@api_bp.route('/predict-v11', methods=['POST'])
def predict_v11():
    """Predicción con modelo v11 avanzado - NLP semántico"""
    try:
        if not MODELO_V11_DISPONIBLE:
            return jsonify({
                "error": "Modelo v11 no disponible en este momento",
                "message": "El modelo avanzado no está cargado"
            }), 503
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": "No se enviaron datos",
                "message": "Por favor envía los síntomas para analizar"
            }), 400
        
        # Obtener parámetros
        symptoms_spanish = data.get('symptoms', '')
        age = data.get('age', 30)
        gender_input = data.get('gender')
        
        if not symptoms_spanish or len(symptoms_spanish.strip()) < 3:
            return jsonify({
                "error": "Síntomas insuficientes",
                "message": "Por favor describe tus síntomas con más detalle (mínimo 3 caracteres)"
            }), 400
        
        # 1. Extraer edad del texto si no se proporciona
        try:
            extracted_age = translator_manager.extract_age_from_text(symptoms_spanish)
            if extracted_age:
                age = extracted_age
        except:
            pass
        
        # 2. Categorizar edad
        try:
            age_range = translator_manager.categorize_age(age)
        except:
            age_range = "Unknown"
        
        # 3. Determinar género
        if gender_input:
            try:
                gender = validate_gender(gender_input)
                gender_origin = "manual"
            except:
                gender = "Unknown"
                gender_origin = "manual"
        else:
            try:
                gender = translator_manager.detect_gender(symptoms_spanish)
                gender_origin = "detectado"
            except:
                gender = "Unknown"
                gender_origin = "detectado"
        
        # 4. Realizar predicción con modelo v11
        result = model_manager_v11.predict_v11(symptoms_spanish, age_range, gender)
        
        if "error" in result:
            return jsonify({
                "error": result["error"],
                "message": "Error procesando con modelo v11"
            }), 500
        
        # 5. Traducir diagnóstico principal al español
        try:
            diagnosis_spanish = translator_manager.translate_to_spanish(result["diagnostico_principal"])
        except:
            diagnosis_spanish = result["diagnostico_principal"]
        
        # 6. Traducir top diagnósticos al español
        top_diagnosticos_es = []
        for diag in result.get("top_diagnosticos", []):
            try:
                diag_es = translator_manager.translate_to_spanish(diag["diagnostico"])
            except:
                diag_es = diag["diagnostico"]
            
            top_diagnosticos_es.append({
                "diagnostico": diag_es,
                "diagnostico_original": diag["diagnostico"],
                "confianza": diag["confianza"],
                "confianza_pct": diag["confianza_pct"]
            })
        
        # 7. Generar recomendaciones desde BD
        try:
            recommendations = generate_recommendations(result["diagnostico_principal"], result["confianza"] * 100)
        except:
            recommendations = ["Consulta con un profesional médico"]
        
        # 8. LOG EN BASE DE DATOS (opcional)
        logged_to_db = False
        try:
            from src.database import db_manager
            db_manager.log_prediction(
                symptoms=symptoms_spanish,
                diagnosis=result["diagnostico_principal"],
                confidence=result["confianza"] * 100,
                model_version="v11",
                age_detected=age,
                age_range=age_range,
                gender=gender,
                gender_origin=gender_origin,
                symptoms_processed=result["procesamiento"]["texto_procesado"]
            )
            logged_to_db = True
        except Exception as e:
            logging.error(f"Error logging to DB: {e}")
        
        return jsonify({
            "success": True,
            "result": {
                # Información principal
                "diagnostico": diagnosis_spanish,
                "diagnostico_original": result["diagnostico_principal"],
                "confianza": round(result["confianza"] * 100, 1),
                "confianza_pct": result["confianza_pct"],
                
                # Top diagnósticos
                "top_diagnosticos": top_diagnosticos_es,
                
                # Información del paciente
                "edad_detectada": age,
                "rango_edad": age_range,
                "genero_usado": gender,
                "genero_origen": gender_origin,
                
                # Información del modelo
                "modelo_usado": "v11",
                "idioma_detectado": result["idioma_detectado"],
                
                # Procesamiento
                "sintomas_procesados": result["procesamiento"]["texto_procesado"],
                "embeddings_generados": result["procesamiento"]["embeddings_generados"],
                
                # Recomendaciones
                "recomendaciones": recommendations,
                
                # Metadata
                "timestamp": pd.Timestamp.now().isoformat(),
                "logged_to_db": logged_to_db
            },
            "metadata": {
                "modelo_version": result["modelo_version"],
                "procesamiento_avanzado": {
                    "nlp_semantico": "Sentence-BERT + TF-IDF",
                    "diccionario_medico": "Bilingüe ES/EN",
                    "deteccion_idioma": result["idioma_detectado"],
                    "variables_demograficas": f"Edad: {age_range}, Género: {gender}",
                    "embeddings_384d": result["procesamiento"]["embeddings_generados"]
                }
            }
        })
        
    except Exception as e:
        logging.error(f"Error en /predict-v11: {e}")
        return jsonify({
            "error": str(e),
            "message": "Error interno del servidor en modelo v11"
        }), 500

# ========== INFORMACIÓN MODELO V11 ==========
@api_bp.route('/model-v11-info', methods=['GET'])
def model_v11_info():
    """Información detallada del modelo v11"""
    try:
        if not MODELO_V11_DISPONIBLE:
            return jsonify({
                "available": False,
                "error": "Modelo v11 no está disponible"
            })
        
        info = model_manager_v11.get_model_info()
        
        return jsonify({
            "available": True,
            "model_info": info,
            "capabilities": {
                "nlp_avanzado": "Sentence-BERT + TF-IDF híbrido",
                "idiomas": ["Español", "Inglés"],
                "diccionario_medico": "Términos médicos bilingües",
                "variables_demograficas": "Edad y género",
                "embeddings_semanticos": "384 dimensiones",
                "top_diagnosticos": "3 predicciones principales"
            },
            "endpoint": "/api/predict-v11",
            "parametros": {
                "symptoms": "string (requerido) - Síntomas en español",
                "age": "int (opcional) - Edad del paciente",
                "gender": "string (opcional) - Male/Female/Masculino/Femenino"
            }
        })
        
    except Exception as e:
        return jsonify({
            "available": False,
            "error": str(e)
        }), 500

# ========== ENDPOINTS EXISTENTES (MANTENER) ==========

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
        age = data.get('age', 30)
        gender_input = data.get('gender')
        model_version = data.get('model', 'v8')
        
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
        
        # 3. Determinar género
        if gender_input:
            gender = validate_gender(gender_input)
            gender_origin = "manual"
        else:
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
        try:
            from src.database import db_manager
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
            logged_to_db = True
        except:
            logged_to_db = False
        
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
                "logged_to_db": logged_to_db
            },
            "metadata": {
                "procesamiento": {
                    "traduccion_sintomas": "es → en",
                    "traduccion_diagnostico": "en → es", 
                    "categorizacion_edad": f"{age} → {age_range}",
                    "determinacion_genero": f"{'Manual: ' + str(gender_input) if gender_input else 'Auto-detectado'} → {gender}",
                    "recomendaciones_source": "database"
                }
            }
        })
        
    except Exception as e:
        logging.error(f"Error en /predict-friendly: {e}")
        return jsonify({
            "error": str(e),
            "message": "Error interno del servidor"
        }), 500

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
    """Obtener información de modelos disponibles (ACTUALIZADO con v11)"""
    modelos_base = model_manager.get_available_models()
    
    if MODELO_V11_DISPONIBLE:
        try:
            modelos_todos = model_manager_v11.get_available_models()
        except:
            modelos_todos = modelos_base
    else:
        modelos_todos = modelos_base
    
    descripciones = {
        "v6": "Modelo base XGBoost (rápido)",
        "v7": "Modelo ensemble (alta precisión)",
        "v8": "Modelo expandido (más enfermedades)",
        "v8_mejorado": "Modelo v8 optimizado",
        "v9": "Modelo síntomas binarios (máxima precisión)",
        "v11": "🚀 Modelo avanzado NLP semántico con Sentence-BERT (NUEVO)"
    }
    
    return jsonify({
        "available_models": modelos_todos,
        "total": len(modelos_todos),
        "recommended": "v11" if "v11" in modelos_todos else "v9",
        "newest": "v11",
        "descriptions": descripciones,
        "endpoints": {
            "v11": "/api/predict-v11",
            "others": "/api/predict-friendly"
        }
    })

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Verificar estado de la API"""
    modelo_v11_status = False
    if MODELO_V11_DISPONIBLE:
        try:
            modelo_v11_status = model_manager_v11.modelo_v11 is not None and model_manager_v11.modelo_v11.modelo_xgb is not None
        except:
            pass
    
    return jsonify({
        "status": "healthy",
        "models_loaded": len(model_manager.models),
        "available_models": model_manager.get_available_models(),
        "translator_ready": True,
        "modelo_v11": "loaded" if modelo_v11_status else "unavailable"
    })

# ========== FUNCIONES AUXILIARES ==========

def validate_gender(gender_input):
    """Validar y normalizar entrada de género"""
    if not gender_input:
        return "Unknown"
    
    gender_lower = str(gender_input).lower().strip()
    
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

def generate_recommendations(diagnosis, confidence):
    """Generar recomendaciones desde la base de datos"""
    
    # 1. Obtener recomendaciones de la BD
    try:
        from src.database import db_manager
        db_recommendations = db_manager.get_recommendations(diagnosis)
    except:
        db_recommendations = []
    
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

# ========== ENDPOINTS DE DEBUG (MANTENER) ==========

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
    
    if 'tfidf_vectorizer' in prep:
        tfidf = prep['tfidf_vectorizer']
        debug_info['preprocessors']['tfidf'] = {
            "features_count": tfidf.get_feature_names_out().shape[0],
            "vocabulary_size": len(tfidf.vocabulary_),
            "max_features": getattr(tfidf, 'max_features', 'None')
        }
    
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
        from src.database import db_manager
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

@api_bp.route('/verify-recommendations', methods=['GET'])
def verify_recommendations():
    """Verificar estado de recomendaciones en BD"""
    try:
        from src.database import db_manager
        if not db_manager.connect():
            return jsonify({"error": "No se pudo conectar a BD"}), 500
        
        cursor = db_manager.connection.cursor()
        
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