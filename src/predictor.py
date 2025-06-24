import joblib
import pandas as pd
import numpy as np
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from scipy.sparse import hstack
import warnings
warnings.filterwarnings('ignore')

class SaludIAPredictor:
    """Predictor principal para modelos v7 y v8"""
    
    def __init__(self, model_version='v8'):
        self.model_version = model_version  
        self.model = None
        self.vectorizer = None
        self.age_encoder = None
        self.gender_encoder = None
        self.label_encoder = None
        
        # Rutas de archivos del modelo
        base_path = os.path.join(os.path.dirname(__file__), '..', 'models')
        
        if model_version == 'v7':
            self.model_files = {
                'model': os.path.join(base_path, 'modelo_diagnostico_v7_optimizado.pkl'),
                'preprocessors': os.path.join(base_path, 'preprocesadores_v7.pkl')
            }
        else:  # v8 por defecto
            self.model_files = {
                'model': os.path.join(base_path, 'modelo_diagnostico_v8_reentrenado.pkl'),
                'preprocessors': os.path.join(base_path, 'preprocesadores_v8_reentrenado.pkl')
            }
        
        self._load_models()
    
    def _load_models(self):
        """Cargar todos los componentes del modelo"""
        try:
            print(f"🔄 Cargando modelo {self.model_version}...")
            
            # Verificar archivos
            missing_files = []
            for name, path in self.model_files.items():
                if not os.path.exists(path):
                    missing_files.append(f"{name}: {path}")
            
            if missing_files:
                print(f"❌ Archivos faltantes del modelo {self.model_version}:")
                for file in missing_files:
                    print(f"   - {file}")
                return False
            
            # Cargar modelo
            self.model = joblib.load(self.model_files['model'])
            
            # Cargar preprocesadores
            preprocessors = joblib.load(self.model_files['preprocessors'])
            
            if isinstance(preprocessors, dict):
                self.vectorizer = preprocessors.get('tfidf_vectorizer')
                self.age_encoder = preprocessors.get('age_encoder')
                self.gender_encoder = preprocessors.get('gender_encoder')
                self.label_encoder = preprocessors.get('diagnosis_encoder')
            else:
                # Formato legacy (lista/tuple)
                self.vectorizer = preprocessors[0] if len(preprocessors) > 0 else None
                self.age_encoder = preprocessors[1] if len(preprocessors) > 1 else None
                self.gender_encoder = preprocessors[2] if len(preprocessors) > 2 else None
                self.label_encoder = preprocessors[3] if len(preprocessors) > 3 else None
            
            print(f"✅ Modelo {self.model_version} cargado exitosamente")
            if self.label_encoder:
                print(f"📊 Clases disponibles: {len(self.label_encoder.classes_)}")
            
            return True
            
        except Exception as e:
            print(f"❌ Error cargando modelo {self.model_version}: {e}")
            return False
    
    def predict(self, symptoms, age_range, gender):
        """Realizar predicción médica"""
        try:
            if not all([self.model, self.vectorizer, self.age_encoder, self.gender_encoder]):
                return {
                    'success': False,
                    'error': f'Modelo {self.model_version} no está cargado correctamente'
                }
            
            # Procesar entrada
            symptoms_processed = self._preprocess_symptoms(symptoms)
            symptoms_tfidf = self.vectorizer.transform([symptoms_processed])
            
            # Codificar características demográficas
            try:
                age_encoded = self.age_encoder.transform([age_range])
                gender_encoded = self.gender_encoder.transform([gender])
            except ValueError as e:
                return {
                    'success': False,
                    'error': f'Valor demográfico no reconocido: {str(e)}'
                }
            
            # Combinar características
            features = hstack([symptoms_tfidf, age_encoded.reshape(1, -1), gender_encoded.reshape(1, -1)])
            
            # Hacer predicción
            prediction = self.model.predict(features)[0]
            probabilities = self.model.predict_proba(features)[0]
            
            # Obtener diagnóstico principal
            main_diagnosis = self.label_encoder.inverse_transform([prediction])[0]
            confidence = float(max(probabilities) * 100)
            
            # Top 5 predicciones
            top_indices = np.argsort(probabilities)[::-1][:5]
            top_predictions = []
            
            for idx in top_indices:
                disease = self.label_encoder.inverse_transform([idx])[0]
                prob = float(probabilities[idx] * 100)
                top_predictions.append({
                    'disease': disease,
                    'probability': round(prob, 2)
                })
            
            # Nivel de confianza
            confidence_level = self._get_confidence_level(confidence)
            
            return {
                'success': True,
                'main_diagnosis': main_diagnosis,
                'confidence': round(confidence, 2),
                'confidence_level': confidence_level,
                'top_predictions': top_predictions,
                'processed_symptoms': symptoms_processed,
                'model_version': self.model_version
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error en predicción: {str(e)}'
            }
    
    def _preprocess_symptoms(self, symptoms):
        """Preprocesar síntomas"""
        if isinstance(symptoms, list):
            symptoms = ' '.join(symptoms)
        
        # Limpiar y normalizar
        symptoms = str(symptoms).lower().strip()
        
        # Remover caracteres especiales pero mantener espacios
        import re
        symptoms = re.sub(r'[^\w\s]', ' ', symptoms)
        symptoms = re.sub(r'\s+', ' ', symptoms)
        
        return symptoms
    
    def _get_confidence_level(self, confidence):
        """Determinar nivel de confianza"""
        if confidence >= 90:
            return "Muy Alta"
        elif confidence >= 75:
            return "Alta"
        elif confidence >= 60:
            return "Media"
        elif confidence >= 45:
            return "Baja"
        else:
            return "Muy Baja"


class SaludIAPredictorV9:
    """🆕 Predictor específico para modelo v9 (síntomas binarios)"""
    
    def __init__(self):
        self.model = None
        self.preprocessors = None
        self.diagnosis_encoder = None
        self.feature_columns = []
        
        # Rutas de archivos del modelo v9
        base_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'models_v9_final')
        self.model_files = {
            'model': os.path.join(base_path, 'modelo_diagnostico_v9_final.pkl'),
            'preprocessors': os.path.join(base_path, 'preprocesadores_v9_final.pkl')
        }
        
        self._load_model()
    
    def _load_model(self):
        """Cargar modelo v9 y preprocesadores"""
        try:
            print("🔄 Cargando modelo v9...")
            
            # Verificar archivos
            missing_files = []
            for name, path in self.model_files.items():
                if not os.path.exists(path):
                    missing_files.append(f"{name}: {path}")
            
            if missing_files:
                print("❌ Archivos faltantes del modelo v9:")
                for file in missing_files:
                    print(f"   - {file}")
                return False
            
            # Cargar modelo y preprocesadores
            self.model = joblib.load(self.model_files['model'])
            self.preprocessors = joblib.load(self.model_files['preprocessors'])
            
            # Extraer componentes del preprocesador
            if isinstance(self.preprocessors, dict):
                self.diagnosis_encoder = self.preprocessors.get('diagnosis_encoder')
                self.feature_columns = self.preprocessors.get('feature_columns', [])
                model_info = self.preprocessors.get('model_info', {})
                
                print("✅ Modelo v9 cargado exitosamente")
                print(f"📊 Síntomas soportados: {len(self.feature_columns)}")
                print(f"🏥 Enfermedades: {len(self.diagnosis_encoder.classes_) if self.diagnosis_encoder else 'N/A'}")
                print(f"🎯 Precisión reportada: {model_info.get('accuracy', 'N/A')}")
                
                return True
            else:
                print("❌ Formato de preprocesadores no reconocido")
                return False
                
        except Exception as e:
            print(f"❌ Error cargando modelo v9: {e}")
            return False
    
    def get_symptoms_list(self):
        """Obtener lista completa de síntomas soportados"""
        return self.feature_columns
    
    def predict(self, symptoms_dict):
        """
        Realizar predicción con síntomas binarios
        
        Args:
            symptoms_dict: Dict con síntomas como keys y 0/1 como values
                         Ejemplo: {'itching': 1, 'skin_rash': 1, 'fever': 0}
        """
        try:
            if not self.model or not self.diagnosis_encoder or not self.feature_columns:
                return {
                    'success': False,
                    'error': 'Modelo v9 no está cargado correctamente'
                }
            
            # Crear vector de características
            features = []
            for symptom in self.feature_columns:
                features.append(symptoms_dict.get(symptom, 0))
            
            features_array = np.array(features).reshape(1, -1)
            
            # Hacer predicción
            prediction_idx = self.model.predict(features_array)[0]
            probabilities = self.model.predict_proba(features_array)[0]
            
            # Obtener diagnóstico principal
            main_diagnosis = self.diagnosis_encoder.inverse_transform([prediction_idx])[0]
            confidence = float(probabilities[prediction_idx] * 100)
            
            # Top 5 predicciones
            top_indices = np.argsort(probabilities)[::-1][:5]
            top_predictions = []
            
            for idx in top_indices:
                disease = self.diagnosis_encoder.inverse_transform([idx])[0]
                prob = float(probabilities[idx] * 100)
                if prob > 0.01:  # Solo mostrar probabilidades > 0.01%
                    top_predictions.append({
                        'disease': disease,
                        'probability': round(prob, 2)
                    })
            
            # Nivel de confianza
            confidence_level = self._get_confidence_level(confidence)
            
            # Síntomas activos
            active_symptoms = [symptom for symptom, value in symptoms_dict.items() if value == 1]
            
            return {
                'success': True,
                'main_diagnosis': main_diagnosis,
                'confidence': round(confidence, 2),
                'confidence_level': confidence_level,
                'top_predictions': top_predictions,
                'active_symptoms': active_symptoms,
                'total_symptoms_checked': len(symptoms_dict),
                'model_version': 'v9'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Error en predicción v9: {str(e)}'
            }
    
    def _get_confidence_level(self, confidence):
        """Determinar nivel de confianza para v9"""
        if confidence >= 95:
            return "Muy Alta"
        elif confidence >= 85:
            return "Alta"
        elif confidence >= 70:
            return "Media"
        elif confidence >= 50:
            return "Baja"
        else:
            return "Muy Baja"


# 🔧 INSTANCIAS GLOBALES
try:
    # Cargar modelo principal (v8 por defecto)
    predictor = SaludIAPredictor(model_version='v8')
    print("✅ Predictor v8 inicializado")
except Exception as e:
    print(f"⚠️ Error inicializando predictor v8: {e}")
    predictor = None

try:
    # Cargar modelo v9
    predictor_v9 = SaludIAPredictorV9()
    print("✅ Predictor v9 inicializado") 
except Exception as e:
    print(f"⚠️ Error inicializando predictor v9: {e}")
    predictor_v9 = None

# También mantener v7 disponible
try:
    predictor_v7 = SaludIAPredictor(model_version='v7')
    print("✅ Predictor v7 inicializado")
except Exception as e:
    print(f"⚠️ Error inicializando predictor v7: {e}")
    predictor_v7 = None