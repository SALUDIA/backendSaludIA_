from flask import Blueprint, request, jsonify
import pandas as pd
import numpy as np
import joblib
import os
import logging
from datetime import datetime
import traceback

# Crear Blueprint para las rutas de predicción
predictor_bp = Blueprint('predictor', __name__)

# Variables globales para los modelos
predictor = None
predictor_v9 = None

def find_model_files():
    """Buscar archivos de modelo disponibles con rutas correctas"""
    model_paths = {}
    
    # 📁 RUTAS CORRECTAS basadas en tu estructura de archivos
    base_models_dir = 'models'  # ← Desde Backend/
    
    # Archivos específicos que existen en tu sistema
    model_files = {
        'v8_model': 'modelo_diagnostico_v8_reentrenado.pkl',
        'v8_preprocessor': 'preprocesadores_v8_reentrenado.pkl',
        'v9_model': 'models_v9_final/modelo_diagnostico_v9_final.pkl',
        'v9_preprocessor': 'models_v9_final/preprocesadores_v9_final.pkl',
        'v7_model': 'modelo_diagnostico_v7_optimizado.pkl',
        'v7_preprocessor': 'preprocesadores_v7.pkl'
    }
    
    print(f"🔍 Buscando modelos en: {os.path.abspath(base_models_dir)}")
    
    if not os.path.exists(base_models_dir):
        print(f"❌ Carpeta 'models' no encontrada en: {os.path.abspath(base_models_dir)}")
        return model_paths
    
    # Verificar cada archivo específico
    for key, filename in model_files.items():
        full_path = os.path.join(base_models_dir, filename)
        
        if os.path.exists(full_path):
            model_paths[key] = full_path
            size = os.path.getsize(full_path) / (1024 * 1024)  # MB
            print(f"✅ Encontrado {key}: {filename} ({size:.1f} MB)")
        else:
            print(f"❌ No encontrado {key}: {filename}")
            print(f"   Buscado en: {os.path.abspath(full_path)}")
    
    # Mostrar archivos disponibles para debug
    print(f"\n📋 Archivos .pkl disponibles en models/:")
    try:
        for root, dirs, files in os.walk(base_models_dir):
            for file in files:
                if file.endswith('.pkl'):
                    rel_path = os.path.relpath(os.path.join(root, file), base_models_dir)
                    full_path = os.path.join(root, file)
                    size = os.path.getsize(full_path) / (1024 * 1024)
                    print(f"   📄 {rel_path} ({size:.1f} MB)")
    except Exception as e:
        print(f"   ❌ Error listando archivos: {e}")
    
    return model_paths

class DiagnosticPredictor:
    """Predictor para diagnósticos médicos v8"""
    
    def __init__(self):
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self.scaler = None
        self.loaded = False
        self.error_message = ""
        
    def load_models(self):
        """Cargar modelos v8 con rutas correctas"""
        try:
            print("🔄 Cargando modelo v8...")
            
            # Buscar archivos de modelo
            model_paths = find_model_files()
            
            if 'v8_model' not in model_paths:
                self.error_message = "Archivo modelo_diagnostico_v8_reentrenado.pkl no encontrado"
                print(f"❌ {self.error_message}")
                return False
                
            if 'v8_preprocessor' not in model_paths:
                self.error_message = "Archivo preprocesadores_v8_reentrenado.pkl no encontrado"
                print(f"❌ {self.error_message}")
                return False
            
            # Cargar modelo
            model_path = model_paths['v8_model']
            print(f"📁 Cargando modelo v8 desde: {model_path}")
            self.model = joblib.load(model_path)
            print("   ✅ Modelo v8 cargado exitosamente")
            
            # Cargar preprocesadores
            preprocessor_path = model_paths['v8_preprocessor']
            print(f"📁 Cargando preprocesadores v8 desde: {preprocessor_path}")
            preprocessors = joblib.load(preprocessor_path)
            
            # Verificar estructura de preprocesadores
            if isinstance(preprocessors, dict):
                self.vectorizer = preprocessors.get('vectorizer')
                self.label_encoder = preprocessors.get('label_encoder')
                self.scaler = preprocessors.get('scaler')
                
                print(f"   📦 Componentes encontrados:")
                print(f"      - Vectorizer: {'✅' if self.vectorizer else '❌'}")
                print(f"      - Label Encoder: {'✅' if self.label_encoder else '❌'}")
                print(f"      - Scaler: {'✅' if self.scaler else '❌'}")
            else:
                # Si no es un diccionario, asumir que es solo el vectorizer
                self.vectorizer = preprocessors
                print("   ⚠️ Solo vectorizer encontrado (archivo no es diccionario)")
            
            if not self.vectorizer:
                self.error_message = "Vectorizer no encontrado en preprocesadores"
                print(f"❌ {self.error_message}")
                return False
            
            print("   ✅ Preprocesadores v8 cargados exitosamente")
            
            self.loaded = True
            return True
            
        except Exception as e:
            self.error_message = f"Error cargando modelo v8: {str(e)}"
            print(f"❌ {self.error_message}")
            traceback.print_exc()
            self.loaded = False
            return False
    
    def predict(self, symptoms_text, age=None, gender=None):
        """Realizar predicción v8"""
        if not self.loaded:
            return {"error": f"Modelo v8 no cargado: {self.error_message}"}
            
        try:
            # Procesar síntomas
            symptoms_vector = self.vectorizer.transform([symptoms_text])
            
            # Agregar características adicionales si están disponibles
            if age is not None and gender is not None and self.scaler:
                additional_features = np.array([[age, 1 if gender.lower() in ['masculino', 'male', 'm'] else 0]])
                additional_features = self.scaler.transform(additional_features)
                symptoms_vector = np.hstack([symptoms_vector.toarray(), additional_features])
            
            # Predicción
            prediction = self.model.predict(symptoms_vector)[0]
            probability = self.model.predict_proba(symptoms_vector)[0]
            
            # Decodificar resultado si hay label_encoder
            if self.label_encoder:
                diagnosis = self.label_encoder.inverse_transform([prediction])[0]
            else:
                diagnosis = str(prediction)  # Usar predicción directa
            
            confidence = float(max(probability))
            
            return {
                "diagnosis": diagnosis,
                "confidence": confidence,
                "model_version": "v8",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Error en predicción v8: {str(e)}"
            print(f"❌ {error_msg}")
            traceback.print_exc()
            return {"error": error_msg}

class PredictorV9:
    """Predictor para síntomas binarios v9"""
    
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.loaded = False
        self.error_message = ""
        
    def load_model(self):
        """Cargar modelo v9 con rutas correctas"""
        try:
            print("🔄 Cargando modelo v9...")
            
            model_paths = find_model_files()
            
            if 'v9_model' not in model_paths:
                self.error_message = "Archivo modelo_diagnostico_v9_final.pkl no encontrado"
                print(f"❌ {self.error_message}")
                return False
            
            # Cargar modelo v9
            model_path = model_paths['v9_model']
            print(f"📁 Cargando modelo v9 desde: {model_path}")
            self.model = joblib.load(model_path)
            print("   ✅ Modelo v9 cargado exitosamente")
            
            # Cargar preprocesador v9 si existe
            if 'v9_preprocessor' in model_paths:
                preprocessor_path = model_paths['v9_preprocessor']
                print(f"📁 Cargando preprocesador v9 desde: {preprocessor_path}")
                self.preprocessor = joblib.load(preprocessor_path)
                print("   ✅ Preprocesador v9 cargado")
            else:
                print("   ⚠️ No se encontró preprocesador v9 (opcional)")
            
            self.loaded = True
            return True
            
        except Exception as e:
            self.error_message = f"Error cargando modelo v9: {str(e)}"
            print(f"❌ {self.error_message}")
            traceback.print_exc()
            self.loaded = False
            return False
    
    def predict(self, symptoms_binary):
        """Realizar predicción v9"""
        if not self.loaded:
            return {"error": f"Modelo v9 no cargado: {self.error_message}"}
            
        try:
            # Convertir a array numpy
            symptoms_array = np.array(symptoms_binary).reshape(1, -1)
            
            # Aplicar preprocesador si existe
            if self.preprocessor:
                symptoms_array = self.preprocessor.transform(symptoms_array)
            
            # Predicción
            prediction = self.model.predict(symptoms_array)[0]
            probability = self.model.predict_proba(symptoms_array)[0]
            
            return {
                "diagnosis": str(prediction),
                "confidence": float(max(probability)),
                "model_version": "v9",
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            error_msg = f"Error en predicción v9: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}

# Inicializar predictores globales
def initialize_predictors():
    """Inicializar todos los predictores"""
    global predictor, predictor_v9
    
    print("🤖 Inicializando predictores...")
    print(f"📁 Directorio de trabajo: {os.getcwd()}")
    print(f"📁 Directorio models existe: {os.path.exists('models')}")
    
    # Predictor v8
    predictor = DiagnosticPredictor()
    v8_success = predictor.load_models()
    
    # Predictor v9
    predictor_v9 = PredictorV9()
    v9_success = predictor_v9.load_model()
    
    print(f"\n📊 ESTADO FINAL DE MODELOS:")
    print(f"   V8: {'✅ CARGADO' if v8_success else '❌ FALLO'}")
    print(f"   V9: {'✅ CARGADO' if v9_success else '❌ FALLO'}")
    
    if v8_success or v9_success:
        print(f"🎉 Al menos un modelo se cargó correctamente")
    else:
        print("⚠️ ADVERTENCIA: Ningún modelo se cargó correctamente")
        print("💡 Verificar que los archivos estén en la carpeta 'models/'")
    
    print("✅ Inicialización de predictores completada")

# [Mantener todas las rutas del Blueprint igual...]
@predictor_bp.route('/predict-friendly', methods=['POST'])
def predict_friendly():
    """Endpoint para predicción amigable (v8)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se enviaron datos"}), 400
        
        symptoms = data.get('symptoms', '')
        age = data.get('age')
        gender = data.get('gender')
        
        if not symptoms:
            return jsonify({"error": "Se requiere el campo 'symptoms'"}), 400
        
        # Verificar que el predictor esté disponible
        if not predictor or not predictor.loaded:
            return jsonify({
                "error": "Modelo v8 no disponible",
                "details": predictor.error_message if predictor else "Predictor no inicializado",
                "suggestion": "Verificar que los archivos modelo_diagnostico_v8_reentrenado.pkl y preprocesadores_v8_reentrenado.pkl estén en 'models/'"
            }), 503
        
        # Realizar predicción
        result = predictor.predict(symptoms, age, gender)
        
        if "error" in result:
            return jsonify(result), 500
        
        return jsonify({
            "success": True,
            "prediction": result,
            "message": "Predicción realizada exitosamente"
        })
        
    except Exception as e:
        logging.error(f"Error en predict-friendly: {e}")
        traceback.print_exc()
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@predictor_bp.route('/model-status', methods=['GET'])
def model_status():
    """Verificar estado de los modelos"""
    return jsonify({
        "working_directory": os.getcwd(),
        "models_directory_exists": os.path.exists('models'),
        "v8_model": {
            "loaded": predictor.loaded if predictor else False,
            "error": predictor.error_message if predictor else "No inicializado"
        },
        "v9_model": {
            "loaded": predictor_v9.loaded if predictor_v9 else False,
            "error": predictor_v9.error_message if predictor_v9 else "No inicializado"
        }
    })

@predictor_bp.route('/predict', methods=['POST'])
def predict_technical():
    """Endpoint para predicción técnica (v8)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se enviaron datos"}), 400
        
        symptoms = data.get('symptoms', '')
        
        if not symptoms:
            return jsonify({"error": "Se requiere el campo 'symptoms'"}), 400
        
        if not predictor or not predictor.loaded:
            return jsonify({
                "error": "Modelo v8 no disponible",
                "details": predictor.error_message if predictor else "Predictor no inicializado"
            }), 503
        
        # Realizar predicción
        result = predictor.predict(symptoms)
        
        if "error" in result:
            return jsonify(result), 500
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error en predict: {e}")
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@predictor_bp.route('/predict-v9', methods=['POST'])
def predict_v9():
    """Endpoint para predicción con síntomas binarios (v9)"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No se enviaron datos"}), 400
        
        symptoms_binary = data.get('symptoms_binary', [])
        
        if not symptoms_binary or not isinstance(symptoms_binary, list):
            return jsonify({"error": "Se requiere 'symptoms_binary' como lista"}), 400
        
        if not predictor_v9 or not predictor_v9.loaded:
            return jsonify({
                "error": "Modelo v9 no disponible",
                "details": predictor_v9.error_message if predictor_v9 else "Predictor no inicializado"
            }), 503
        
        # Realizar predicción
        result = predictor_v9.predict(symptoms_binary)
        
        if "error" in result:
            return jsonify(result), 500
        
        return jsonify({
            "success": True,
            "prediction": result,
            "message": "Predicción v9 realizada exitosamente"
        })
        
    except Exception as e:
        logging.error(f"Error en predict-v9: {e}")
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@predictor_bp.route('/symptoms-v9', methods=['GET'])
def get_symptoms_v9():
    """Obtener lista de síntomas para v9"""
    symptoms_list = [
        "fiebre", "tos", "dolor_cabeza", "fatiga", "dolor_garganta",
        "congestion_nasal", "dolor_muscular", "nauseas", "vomito", 
        "diarrea", "dolor_abdominal", "erupciones_piel"
    ]
    
    return jsonify({
        "symptoms": symptoms_list,
        "total": len(symptoms_list),
        "model_version": "v9"
    })

# Inicializar predictores al importar el módulo
initialize_predictors()