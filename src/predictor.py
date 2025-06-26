import joblib
import os
import numpy as np
from datetime import datetime
import logging
from src.preprocessor import FeatureBuilder, PredictionDecoder

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
                    
                    # Mostrar info del modelo
                    self._print_model_info(version, preprocessor)
                else:
                    print(f"   ❌ {version}: Archivos no encontrados")
                    
            except Exception as e:
                print(f"   ❌ {version}: Error - {e}")
        
        print(f"📊 Total modelos cargados: {len(self.models)}")
    
    def _print_model_info(self, version, prep):
        """Mostrar información del modelo cargado"""
        info_parts = []
        
        if 'tfidf_vectorizer' in prep:
            tfidf_features = prep['tfidf_vectorizer'].get_feature_names_out().shape[0]
            info_parts.append(f"TF-IDF: {tfidf_features}")
        
        if 'age_encoder' in prep:
            info_parts.append("Age: ✓")
        
        if 'gender_encoder' in prep:
            info_parts.append("Gender: ✓")
        
        if 'diagnosis_encoder' in prep:
            diseases_count = len(prep['diagnosis_encoder'].classes_)
            info_parts.append(f"Diseases: {diseases_count}")
        
        if 'feature_columns' in prep:
            symptoms_count = len(prep['feature_columns'])
            info_parts.append(f"Symptoms: {symptoms_count}")
        
        print(f"      📋 {' | '.join(info_parts)}")
    
    def get_available_models(self):
        """Obtener lista de modelos disponibles"""
        return list(self.models.keys())
    
    def predict_text(self, text, model_version='v8', age_range=None, gender=None):
        """Predicción para modelos de texto"""
        if model_version not in self.models:
            return {"error": f"Modelo {model_version} no disponible"}
        
        try:
            model_data = self.models[model_version]
            
            # Usar FeatureBuilder para construir características
            feature_builder = FeatureBuilder(model_data)
            features, processed_text = feature_builder.build_text_features(text, age_range, gender)
            
            # Realizar predicción
            model = model_data['model']
            prediction = model.predict(features)[0]
            probabilities = model.predict_proba(features)[0]
            
            # Decodificar resultado
            diagnosis, confidence = PredictionDecoder.decode_prediction(
                prediction, probabilities, model_data['preprocessor']
            )
            
            return {
                "diagnosis": diagnosis,
                "confidence": confidence,
                "model_version": model_version,
                "processed_text": processed_text,
                "features_count": features.shape[1],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logging.error(f"Error en predicción de texto: {e}")
            return {"error": f"Error en predicción: {str(e)}"}
    
    def predict_binary(self, symptoms_array, model_version='v9'):
        """Predicción para modelo binario (v9)"""
        if model_version not in self.models:
            return {"error": f"Modelo {model_version} no disponible"}
        
        try:
            model_data = self.models[model_version]
            
            # Usar FeatureBuilder para construir características
            feature_builder = FeatureBuilder(model_data)
            features = feature_builder.build_binary_features(symptoms_array)
            
            # Realizar predicción
            model = model_data['model']
            prediction = model.predict(features)[0]
            probabilities = model.predict_proba(features)[0]
            
            # Decodificar resultado
            diagnosis, confidence = PredictionDecoder.decode_prediction(
                prediction, probabilities, model_data['preprocessor']
            )
            
            return {
                "diagnosis": diagnosis,
                "confidence": confidence,
                "model_version": model_version,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Error en predicción binaria: {str(e)}"}

# Instancia global del gestor de modelos
model_manager = ModelManager()