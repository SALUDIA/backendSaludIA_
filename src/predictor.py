import joblib
import os
import numpy as np
from datetime import datetime
import logging

class ModelManager:
    """Gestor simplificado de modelos"""
    
    def __init__(self):
        self.models = {}
        self.models_dir = 'models'
        self.load_all_models()
    
    def load_all_models(self):
        """Cargar todos los modelos disponibles"""
        print("🤖 Cargando modelos disponibles...")
        
        # Modelos a cargar con sus archivos
        model_configs = {
            'v6': {
                'model': 'modelo_diagnostico_v6_xgboost.pkl',
                'preprocessor': 'preprocesadores_v6.pkl'
            },
            'v7': {
                'model': 'modelo_diagnostico_v7_optimizado.pkl', 
                'preprocessor': 'preprocesadores_v7.pkl'
            },
            'v8': {
                'model': 'modelo_diagnostico_v8_reentrenado.pkl',
                'preprocessor': 'preprocesadores_v8_reentrenado.pkl'
            },
            'v8_mejorado': {
                'model': 'modelo_diagnostico_v8_mejorado.pkl',
                'preprocessor': 'preprocesadores_v8_mejorado.pkl'
            },
            'v9': {
                'model': 'modelo_diagnostico_v9_final.pkl',
                'preprocessor': 'preprocesadores_v9_final.pkl'
            }
        }
        
        for version, config in model_configs.items():
            try:
                model_path = os.path.join(self.models_dir, config['model'])
                prep_path = os.path.join(self.models_dir, config['preprocessor'])
                
                if os.path.exists(model_path) and os.path.exists(prep_path):
                    model = joblib.load(model_path)
                    preprocessor = joblib.load(prep_path)
                    
                    self.models[version] = {
                        'model': model,
                        'preprocessor': preprocessor,
                        'loaded': True,
                        'type': 'binary' if version == 'v9' else 'text'
                    }
                    print(f"   ✅ {version}: Cargado exitosamente")
                else:
                    print(f"   ❌ {version}: Archivos no encontrados")
                    
            except Exception as e:
                print(f"   ❌ {version}: Error - {e}")
        
        print(f"📊 Total modelos cargados: {len(self.models)}")
    
    def get_available_models(self):
        """Obtener lista de modelos disponibles"""
        return list(self.models.keys())
    
    def predict_text(self, text, model_version='v8', age_range=None, gender=None):
        """Predicción para modelos de texto"""
        if model_version not in self.models:
            return {"error": f"Modelo {model_version} no disponible"}
        
        try:
            model_data = self.models[model_version]
            model = model_data['model']
            prep = model_data['preprocessor']
            
            # Procesar texto
            if 'tfidf_vectorizer' in prep:
                text_features = prep['tfidf_vectorizer'].transform([text])
            else:
                return {"error": "Vectorizador no encontrado"}
            
            # Agregar características demográficas si están disponibles
            features = text_features
            if age_range and gender and 'age_encoder' in prep and 'gender_encoder' in prep:
                try:
                    age_enc = prep['age_encoder'].transform([age_range])[0]
                    gender_enc = prep['gender_encoder'].transform([gender])[0]
                    demo_features = np.array([[age_enc, gender_enc]])
                    from scipy.sparse import hstack
                    features = hstack([text_features, demo_features])
                except:
                    pass  # Usar solo texto si falla
            
            # Predicción
            prediction = model.predict(features)[0]
            probabilities = model.predict_proba(features)[0]
            
            # Decodificar resultado
            if 'diagnosis_encoder' in prep:
                diagnosis = prep['diagnosis_encoder'].inverse_transform([prediction])[0]
            else:
                diagnosis = str(prediction)
            
            return {
                "diagnosis": diagnosis,
                "confidence": float(max(probabilities)) * 100,
                "model_version": model_version,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Error en predicción: {str(e)}"}
    
    def predict_binary(self, symptoms_array, model_version='v9'):
        """Predicción para modelo binario (v9)"""
        if model_version not in self.models:
            return {"error": f"Modelo {model_version} no disponible"}
        
        try:
            model_data = self.models[model_version]
            model = model_data['model']
            prep = model_data['preprocessor']
            
            # Convertir a numpy array
            symptoms = np.array(symptoms_array).reshape(1, -1)
            
            # Predicción
            prediction = model.predict(symptoms)[0]
            probabilities = model.predict_proba(symptoms)[0]
            
            # Decodificar resultado
            if 'diagnosis_encoder' in prep:
                diagnosis = prep['diagnosis_encoder'].inverse_transform([prediction])[0]
            else:
                diagnosis = str(prediction)
            
            return {
                "diagnosis": diagnosis,
                "confidence": float(max(probabilities)) * 100,
                "model_version": model_version,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Error en predicción binaria: {str(e)}"}

# Instancia global del gestor de modelos
model_manager = ModelManager()