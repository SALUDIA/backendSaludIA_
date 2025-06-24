from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
from datetime import datetime
import traceback

# Importar componentes
from .predictor import predictor, predictor_v9, predictor_v7
from .database import db_manager
from .translator import SymptomTranslator
from config.loader import get_config_instance, get_cors_config

import logging

# Configurar logging para producción
if os.getenv('FLASK_ENV') == 'production':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s %(name)s %(message)s'
    )

# Crear app Flask
app = Flask(__name__)

# 🔧 CONFIGURACIÓN CON TODAS LAS VARIABLES DE ENTORNO
try:
    config = get_config_instance()
    cors_config = get_cors_config()
    print("✅ Configuración cargada correctamente")
except Exception as e:
    print(f"⚠️ Error cargando configuración: {e}")
    # Configuración fallback
    cors_config = {
        'origins': ['*'],
        'methods': ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        'allow_headers': ['Content-Type', 'Authorization', 'X-Requested-With'],
        'supports_credentials': False
    }

# Configurar CORS
CORS(app, **cors_config)

# Configurar Flask
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('API_MAX_CONTENT_LENGTH', 16777216))  # 16MB

# 🔧 INICIALIZAR TRADUCTOR GLOBALMENTE
symptom_translator = None
translation_enabled = os.getenv('ENABLE_TRANSLATION', 'true').lower() == 'true'

if translation_enabled:
    try:
        symptom_translator = SymptomTranslator()
        print("✅ Traductor de síntomas inicializado")
    except Exception as e:
        print(f"⚠️ Error inicializando traductor: {e}")
        symptom_translator = None
        translation_enabled = False
else:
    print("ℹ️ Traducción deshabilitada por configuración")

# 🔧 FUNCIONES AUXILIARES PARA predict-friendly
def validate_input_friendly(symptoms, age, gender):
    """Validar entrada para endpoint friendly"""
    errors = []
    
    if not symptoms or not symptoms.strip():
        errors.append("Los síntomas no pueden estar vacíos")
    
    if not isinstance(age, int) or age < 1 or age > 120:
        errors.append("La edad debe ser un número entre 1 y 120")
    
    if not gender or gender.lower() not in ['masculino','femenino', 'male', 'female', 'hombre', 'mujer', 'm', 'f']:
        errors.append("El género debe ser: Masculino, Femenino, male, female, hombre, mujer, m, f")  # ← SIMPLIFICAR MENSAJE
    
    return errors

def get_age_range_from_age(age):
    """Convertir edad numérica a rango"""
    if age < 18:
        return "0-17"
    elif age < 31:
        return "18-30"
    elif age < 41:
        return "31-40"
    elif age < 51:
        return "41-50"
    elif age < 61:
        return "51-60"
    else:
        return "60+"

def normalize_gender(gender):
    """Normalizar género a formato del modelo"""
    gender_lower = gender.lower()
    if gender_lower in ['male', 'hombre', 'm', 'masculino']:  # ← AGREGAR 'masculino'
        return "Male"
    elif gender_lower in ['female', 'mujer', 'f', 'femenino']:  # ← AGREGAR 'femenino'
        return "Female"
    else:
        return gender  # Devolver original si no se puede normalizar

def format_symptoms_for_model(symptoms):
    """Formatear síntomas para el modelo"""
    # Limpiar y formatear texto
    formatted = symptoms.lower().strip()
    # Remover caracteres especiales innecesarios
    formatted = ''.join(char for char in formatted if char.isalnum() or char.isspace())
    return formatted

def validate_input(symptoms, age_range, gender):
    """Validar entrada para endpoint técnico"""
    errors = []
    
    if not symptoms or not symptoms.strip():
        errors.append("Los síntomas no pueden estar vacíos")
    
    valid_age_ranges = ["0-17", "18-30", "31-40", "41-50", "51-60", "60+"]
    if age_range not in valid_age_ranges:
        errors.append(f"Rango de edad inválido. Debe ser uno de: {valid_age_ranges}")
    
    if gender not in ["Male", "Female"]:
        errors.append("El género debe ser 'Male' o 'Female'")
    
    return errors

def add_spanish_translations(resultado):
    """Agregar traducciones al español usando el traductor de base de datos"""
    try:
        # Traducir diagnóstico principal
        if 'main_diagnosis' in resultado:
            spanish_diagnosis = db_manager.translate_disease(resultado['main_diagnosis'])
            if spanish_diagnosis != resultado['main_diagnosis']:
                resultado['main_diagnosis_spanish'] = spanish_diagnosis
        
        # Traducir predicciones top
        if 'top_predictions' in resultado:
            spanish_predictions = []
            for pred in resultado['top_predictions']:
                spanish_pred = pred.copy()
                spanish_disease = db_manager.translate_disease(pred['disease'])
                if spanish_disease != pred['disease']:
                    spanish_pred['disease_spanish'] = spanish_disease
                spanish_predictions.append(spanish_pred)
            resultado['top_predictions_spanish'] = spanish_predictions
        
        return resultado
    except Exception as e:
        print(f"⚠️ Error agregando traducciones: {e}")
        return resultado

# 🏠 ENDPOINT DE BIENVENIDA
@app.route('/', methods=['GET'])
def home():
    """Endpoint de bienvenida"""
    return jsonify({
        'message': '🏥 SaludIA Backend API',
        'version': '2.0',
        'status': 'active',
        'models_available': {
            'v7': predictor_v7 is not None,
            'v8': predictor is not None,
            'v9': predictor_v9 is not None
        },
        'endpoints': {
            'POST /predict': 'Predicción v8 (texto + demografía)',
            'POST /predict-friendly': 'Predicción v8 (amigable + traducción)',
            'POST /predict-v9': 'Predicción v9 (síntomas binarios)',
            'POST /predict-v7': 'Predicción v7 (texto + demografía)',
            'GET /health': 'Estado del servidor',
            'GET /symptoms-v9': 'Lista de síntomas v9'
        },
        'timestamp': datetime.now().isoformat()
    })

# 🔍 HEALTH CHECK
@app.route('/health', methods=['GET'])
def health_check():
    """Estado del servidor"""
    try:
        db_status = db_manager.test_connection()
    except:
        db_status = False
        
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'models': {
            'v7': 'loaded' if predictor_v7 else 'not_loaded',
            'v8': 'loaded' if predictor else 'not_loaded', 
            'v9': 'loaded' if predictor_v9 else 'not_loaded'
        },
        'database': 'connected' if db_status else 'disconnected',
        'translator': 'available' if symptom_translator else 'unavailable'
    })

# 📋 SÍNTOMAS V9
@app.route('/symptoms-v9', methods=['GET'])
def get_symptoms_v9():
    """🆕 Obtener lista de síntomas para modelo v9"""
    if not predictor_v9:
        return jsonify({
            'success': False,
            'error': 'Modelo v9 no disponible'
        }), 503
    
    try:
        symptoms = predictor_v9.get_symptoms_list()
        return jsonify({
            'success': True,
            'total_symptoms': len(symptoms),
            'symptoms': sorted(symptoms),
            'model_version': 'v9',
            'usage': {
                'format': 'binary (0 or 1)',
                'example': {
                    'itching': 1,
                    'skin_rash': 1,
                    'fever': 0
                }
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error obteniendo síntomas: {str(e)}'
        }), 500

# 🚀 ENDPOINT V8 TÉCNICO
@app.route('/predict', methods=['POST'])
def predict_diagnosis():
    """Endpoint técnico v8"""
    session_id = str(uuid.uuid4())
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    user_agent = request.headers.get('User-Agent', '')
    
    try:
        if not predictor:
            return jsonify({
                'success': False,
                'error': 'Modelo v8 no disponible'
            }), 503
        
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No se recibieron datos JSON'
            }), 400
        
        # Validar campos requeridos
        required_fields = ['symptoms', 'age_range', 'gender']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido faltante: {field}',
                    'required_fields': required_fields
                }), 400
        
        # Extraer y validar datos
        symptoms = data['symptoms']
        age_range = data['age_range']
        gender = data['gender']
        
        validation_errors = validate_input(symptoms, age_range, gender)
        if validation_errors:
            return jsonify({
                'success': False,
                'error': 'Datos inválidos',
                'details': validation_errors
            }), 400
        
        # Formatear síntomas
        formatted_symptoms = format_symptoms_for_model(symptoms)
        
        # Hacer predicción
        resultado = predictor.predict(
            symptoms=formatted_symptoms,
            age_range=age_range,
            gender=gender
        )
        
        # Agregar traducción
        resultado = add_spanish_translations(resultado)
        
        # Agregar metadata
        resultado['timestamp'] = datetime.now().isoformat()
        resultado['session_id'] = session_id
        resultado['endpoint_type'] = 'technical'
        
        # Guardar en BD si exitoso
        if resultado.get('success', False):
            consultation_data = {
                'session_id': session_id,
                'symptoms_original': symptoms,
                'symptoms_processed': resultado.get('processed_symptoms', formatted_symptoms),
                'age_range': age_range,
                'gender': gender,
                'main_diagnosis': resultado.get('main_diagnosis', ''),
                'confidence_score': resultado.get('confidence', 0),
                'confidence_level': resultado.get('confidence_level', ''),
                'model_version': 'v8',
                'ip_address': client_ip,
                'user_agent': user_agent
            }
            
            consultation_id = db_manager.save_consultation(consultation_data)
            if consultation_id and 'top_predictions' in resultado:
                original_predictions = [
                    {'disease': pred['disease'], 'probability': pred['probability']}
                    for pred in resultado.get('top_predictions', [])
                ]
                db_manager.save_predictions(consultation_id, original_predictions)
        
        return jsonify(resultado), 200 if resultado.get('success', False) else 500
        
    except Exception as e:
        print(f"❌ Error en /predict: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error del servidor: {str(e)}',
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id
        }), 500

# 🌟 ENDPOINT V8 AMIGABLE CON TRADUCCIÓN
@app.route('/predict-friendly', methods=['POST'])
def predict_diagnosis_friendly():
    """Endpoint amigable v8 con traducción automática"""
    session_id = str(uuid.uuid4())
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    user_agent = request.headers.get('User-Agent', '')
    
    try:
        if not predictor:
            return jsonify({
                'success': False,
                'error': 'Modelo v8 no disponible'
            }), 503
        
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No se recibieron datos JSON'
            }), 400
        
        # Validar campos requeridos
        required_fields = ['symptoms', 'age', 'gender']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido faltante: {field}'
                }), 400
        
        # Extraer datos
        symptoms = data['symptoms']
        age = data['age']
        gender = data['gender']
        
        print(f"🌟 Predict-friendly - Session: {session_id[:8]}...")
        print(f"   Síntomas originales: {symptoms}")
        print(f"   Edad: {age}, Género: {gender}")
        
        # Validar entrada
        validation_errors = validate_input_friendly(symptoms, age, gender)
        if validation_errors:
            return jsonify({
                'success': False,
                'error': 'Datos inválidos',
                'details': validation_errors
            }), 400
        
        # 🌐 TRADUCIR SÍNTOMAS SI HAY TRADUCTOR DISPONIBLE
        translated_symptoms = symptoms
        translation_info = {
            'detected_language': 'unknown',
            'was_translated': False,
            'confidence': 0
        }
        
        if symptom_translator:
            try:
                translation_result = symptom_translator.detect_and_translate(symptoms)
                translated_symptoms = translation_result['translated_text']
                translation_info = {
                    'detected_language': translation_result['detected_language'],
                    'was_translated': translation_result['detected_language'] != 'en',
                    'confidence': translation_result['confidence']
                }
                print(f"🌐 Idioma detectado: {translation_info['detected_language']}")
                print(f"🌐 Síntomas traducidos: {translated_symptoms}")
            except Exception as e:
                print(f"⚠️ Error en traducción: {e}")
                # Continuar sin traducción
        else:
            print("ℹ️ Traductor no disponible, usando síntomas originales")
        
        # Convertir edad a rango
        age_range = get_age_range_from_age(age)
        
        # Normalizar género
        normalized_gender = normalize_gender(gender)
        
        # Formatear síntomas para el modelo
        formatted_symptoms = format_symptoms_for_model(translated_symptoms)
        
        print(f"🔧 Procesado - Edad: {age_range}, Género: {normalized_gender}")
        
        # Hacer predicción
        resultado = predictor.predict(
            symptoms=formatted_symptoms,
            age_range=age_range,
            gender=normalized_gender
        )
        
        # Agregar traducción de resultados
        resultado = add_spanish_translations(resultado)
        
        # Agregar información de procesamiento
        resultado['processing_info'] = {
            'original_input': {
                'symptoms': symptoms,
                'age': age,
                'gender': gender
            },
            'processed_input': {
                'translated_symptoms': translated_symptoms,
                'age_range': age_range,
                'normalized_gender': normalized_gender
            },
            'translation': translation_info
        }
        
        # Metadata adicional
        resultado['timestamp'] = datetime.now().isoformat()
        resultado['session_id'] = session_id
        resultado['endpoint_type'] = 'friendly'
        resultado['user_friendly'] = True
        
        print(f"✅ Predicción completada - Diagnóstico: {resultado.get('main_diagnosis', 'N/A')}")
        
        # Guardar en BD si exitoso
        if resultado.get('success', False):
            consultation_data = {
                'session_id': session_id,
                'symptoms_original': symptoms,
                'symptoms_processed': translated_symptoms,
                'age_range': age_range,
                'gender': normalized_gender,
                'main_diagnosis': resultado.get('main_diagnosis', ''),
                'confidence_score': resultado.get('confidence', 0),
                'confidence_level': resultado.get('confidence_level', ''),
                'model_version': 'v8f',
                'detected_language': translation_info['detected_language'],
                'ip_address': client_ip,
                'user_agent': user_agent
            }
            
            try:
                consultation_id = db_manager.save_consultation(consultation_data)
                if consultation_id and 'top_predictions' in resultado:
                    original_predictions = [
                        {'disease': pred['disease'], 'probability': pred['probability']}
                        for pred in resultado.get('top_predictions', [])
                    ]
                    db_manager.save_predictions(consultation_id, original_predictions)
                    resultado['consultation_id'] = consultation_id
            except Exception as e:
                print(f"⚠️ Error guardando en BD: {e}")
        
        return jsonify(resultado), 200 if resultado.get('success', False) else 500
        
    except Exception as e:
        print(f"❌ Error en /predict-friendly: {e}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'Error del servidor: {str(e)}',
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id
        }), 500

# 🆕 ENDPOINT V9 (SÍNTOMAS BINARIOS)
@app.route('/predict-v9', methods=['POST'])
def predict_diagnosis_v9():
    """🆕 Endpoint v9 con síntomas binarios"""
    session_id = str(uuid.uuid4())
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    user_agent = request.headers.get('User-Agent', '')
    
    try:
        if not predictor_v9:
            return jsonify({
                'success': False,
                'error': 'Modelo v9 no disponible'
            }), 503
        
        data = request.json
        if not data or 'symptoms' not in data:
            return jsonify({
                'success': False,
                'error': 'Campo requerido faltante: symptoms',
                'example': {
                    'symptoms': {
                        'itching': 1,
                        'skin_rash': 1,
                        'fever': 0
                    }
                }
            }), 400
        
        symptoms_dict = data['symptoms']
        
        if not isinstance(symptoms_dict, dict):
            return jsonify({
                'success': False,
                'error': 'El campo symptoms debe ser un diccionario'
            }), 400
        
        # Validar valores binarios
        for symptom, value in symptoms_dict.items():
            if value not in [0, 1]:
                return jsonify({
                    'success': False,
                    'error': f'Valor inválido para síntoma "{symptom}": debe ser 0 o 1'
                }), 400
        
        # Hacer predicción
        resultado = predictor_v9.predict(symptoms_dict)
        
        # Agregar traducción
        resultado = add_spanish_translations(resultado)
        
        # Agregar metadata
        resultado['timestamp'] = datetime.now().isoformat()
        resultado['session_id'] = session_id
        resultado['endpoint_type'] = 'binary_symptoms'
        
        # Guardar en BD si exitoso
        if resultado.get('success', False):
            consultation_data = {
                'session_id': session_id,
                'symptoms_original': str(symptoms_dict),
                'symptoms_processed': f"Binary symptoms: {sum(symptoms_dict.values())} active",
                'age_range': 'Unknown',
                'gender': 'Unknown',
                'main_diagnosis': resultado.get('main_diagnosis', ''),
                'confidence_score': resultado.get('confidence', 0),
                'confidence_level': resultado.get('confidence_level', ''),
                'model_version': 'v9',
                'ip_address': client_ip,
                'user_agent': user_agent
            }
            
            consultation_id = db_manager.save_consultation(consultation_data)
            if consultation_id and 'top_predictions' in resultado:
                original_predictions = [
                    {'disease': pred['disease'], 'probability': pred['probability']}
                    for pred in resultado.get('top_predictions', [])
                ]
                db_manager.save_predictions(consultation_id, original_predictions)
        
        return jsonify(resultado), 200 if resultado.get('success', False) else 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error del servidor: {str(e)}',
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id
        }), 500

# 🔄 ENDPOINT V7 (OPCIONAL)
@app.route('/predict-v7', methods=['POST'])
def predict_diagnosis_v7():
    """Endpoint v7 (modelo original)"""
    session_id = str(uuid.uuid4())
    client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
    user_agent = request.headers.get('User-Agent', '')
    
    try:
        if not predictor_v7:
            return jsonify({
                'success': False,
                'error': 'Modelo v7 no disponible'
            }), 503
        
        data = request.json
        if not data:
            return jsonify({
                'success': False,
                'error': 'No se recibieron datos JSON'
            }), 400
        
        # Misma lógica que v8 pero usando predictor_v7
        required_fields = ['symptoms', 'age_range', 'gender']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'error': f'Campo requerido faltante: {field}'
                }), 400
        
        symptoms = data['symptoms']
        age_range = data['age_range'] 
        gender = data['gender']
        
        validation_errors = validate_input(symptoms, age_range, gender)
        if validation_errors:
            return jsonify({
                'success': False,
                'error': 'Datos inválidos',
                'details': validation_errors
            }), 400
        
        formatted_symptoms = format_symptoms_for_model(symptoms)
        
        # Hacer predicción con v7
        resultado = predictor_v7.predict(
            symptoms=formatted_symptoms,
            age_range=age_range,
            gender=gender
        )
        
        # Agregar traducción
        resultado = add_spanish_translations(resultado)
        
        # Metadata
        resultado['timestamp'] = datetime.now().isoformat()
        resultado['session_id'] = session_id
        resultado['endpoint_type'] = 'v7_legacy'
        
        return jsonify(resultado), 200 if resultado.get('success', False) else 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error del servidor: {str(e)}',
            'timestamp': datetime.now().isoformat(),
            'session_id': session_id
        }), 500

# 📊 ESTADÍSTICAS
@app.route('/stats', methods=['GET'])
def get_stats():
    """Obtener estadísticas del sistema"""
    try:
        stats = db_manager.get_consultation_stats()
        if stats:
            stats['timestamp'] = datetime.now().isoformat()
            return jsonify({
                'success': True,
                'stats': stats
            })
        else:
            return jsonify({
                'success': False,
                'error': 'No se pudieron obtener estadísticas'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error obteniendo estadísticas: {str(e)}'
        }), 500

# 🔧 CONFIGURACIÓN
@app.route('/config', methods=['GET'])
def get_configuration():
    """Obtener configuración actual (sin credenciales sensibles)"""
    try:
        env_info = {
            'environment': os.getenv('FLASK_ENV', 'development'),
            'debug_mode': os.getenv('DEBUG_MODE', 'false').lower() == 'true',
            'model_version': os.getenv('MODEL_VERSION', 'v8'),
            'cors_origins': os.getenv('CORS_ORIGINS', '*'),
            'translation_enabled': translation_enabled,
            'database_logging': os.getenv('ENABLE_DATABASE_LOGGING', 'true').lower() == 'true',
            'v9_model_enabled': os.getenv('ENABLE_V9_MODEL', 'true').lower() == 'true',
            'api_rate_limit': os.getenv('API_RATE_LIMIT', '100 per minute'),
            'ssl_required': os.getenv('DB_SSL_REQUIRED', 'false').lower() == 'true',
            'health_check_enabled': os.getenv('HEALTH_CHECK_ENABLED', 'true').lower() == 'true'
        }
        
        return jsonify({
            'success': True,
            'configuration': env_info,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Error obteniendo configuración: {str(e)}'
        }), 500

# MANEJO DE ERRORES
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 'Endpoint no encontrado',
        'available_endpoints': [
            'POST /predict',
            'POST /predict-friendly', 
            'POST /predict-v9',
            'POST /predict-v7',
            'GET /health',
            'GET /symptoms-v9',
            'GET /stats',
            'GET /config'
        ]
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'success': False,
        'error': 'Error interno del servidor',
        'timestamp': datetime.now().isoformat()
    }), 500

# 🚀 PUNTO DE ENTRADA
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('DEBUG_MODE', 'true').lower() == 'true'
    
    print("🏥 SaludIA Backend API")
    print("=" * 40)
    print(f"🚀 Iniciando en {host}:{port}")
    print(f"🔧 Debug: {debug}")
    print(f"🌐 CORS: {cors_config['origins']}")
    print(f"🤖 Modelo: {os.getenv('MODEL_VERSION', 'v8')}")
    print(f"🌍 Traducción: {'Habilitada' if translation_enabled else 'Deshabilitada'}")
    print("📋 Endpoints disponibles:")
    print("   POST /predict - Técnico v8")
    print("   POST /predict-friendly - Amigable v8 + Traducción 🌟")
    print("   POST /predict-v9 - Síntomas binarios")
    print("   POST /predict-v7 - Modelo original")
    print("   GET /health - Estado del servidor")
    print("=" * 40)
    
    app.run(host=host, port=port, debug=debug)