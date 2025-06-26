import re
import pandas as pd
import numpy as np
from scipy.sparse import hstack
import logging

class TextPreprocessor:
    """Preprocesador de texto médico"""
    
    @staticmethod
    def clean_medical_text(text):
        """Limpiar texto médico"""
        if pd.isna(text) or text == '':
            return 'patient presents with general symptoms'
        
        text = str(text).lower()
        
        # Términos médicos importantes que no deben ser eliminados
        medical_terms = [
            'patient', 'experiences', 'has', 'shows', 'reports', 
            'complains', 'presents', 'symptoms', 'pain', 'fever', 
            'headache', 'nausea', 'chest', 'abdominal', 'breathing'
        ]
        
        # Limpiar caracteres especiales pero conservar espacios
        text = re.sub(r'[^\w\s]', ' ', text)
        text = re.sub(r'\d+', '', text)
        text = re.sub(r'\s+', ' ', text)
        
        # Filtrar palabras muy cortas excepto términos médicos importantes
        words = text.split()
        words = [word for word in words if len(word) >= 3 or word in medical_terms]
        text = ' '.join(words)
        
        # Asegurar que el texto tenga contenido mínimo
        if len(text.split()) < 3:
            text = 'patient presents with general symptoms'
            
        return text.strip()

class FeatureBuilder:
    """Constructor de características para predicción"""
    
    def __init__(self, model_data):
        self.model = model_data['model']
        self.prep = model_data['preprocessor']
        
    def build_text_features(self, text, age_range=None, gender=None):
        """Construir características para modelos de texto"""
        try:
            # 1. Preprocesar texto
            clean_text = TextPreprocessor.clean_medical_text(text)
            
            # 2. Vectorizar texto con TF-IDF
            if 'tfidf_vectorizer' not in self.prep:
                raise ValueError("TF-IDF vectorizador no encontrado")
                
            tfidf = self.prep['tfidf_vectorizer']
            text_features = tfidf.transform([clean_text])
            
            # 3. Agregar características demográficas si el modelo las requiere
            if 'age_encoder' in self.prep and 'gender_encoder' in self.prep:
                age_encoder = self.prep['age_encoder']
                gender_encoder = self.prep['gender_encoder']
                
                # Usar valores por defecto
                if not age_range:
                    age_range = "25-34"
                if not gender:
                    gender = "Unknown"
                
                # Validar y corregir categorías
                if age_range not in age_encoder.classes_:
                    age_range = age_encoder.classes_[0]
                    
                if gender not in gender_encoder.classes_:
                    gender = gender_encoder.classes_[0]
                
                # Codificar
                age_enc = age_encoder.transform([age_range])[0]
                gender_enc = gender_encoder.transform([gender])[0]
                
                # Combinar características
                demo_features = np.array([[age_enc, gender_enc]])
                combined_features = hstack([text_features, demo_features])
                
                logging.info(f"Características: TF-IDF({text_features.shape[1]}) + Demo(2) = {combined_features.shape[1]}")
                
                return combined_features, clean_text
            else:
                return text_features, clean_text
                
        except Exception as e:
            logging.error(f"Error construyendo características: {e}")
            raise
    
    def build_binary_features(self, symptoms_array):
        """Construir características para modelo binario"""
        try:
            # Validar longitud esperada
            if 'feature_columns' in self.prep:
                expected_length = len(self.prep['feature_columns'])
                if len(symptoms_array) != expected_length:
                    raise ValueError(f"Se esperan {expected_length} síntomas, recibidos {len(symptoms_array)}")
            
            return np.array(symptoms_array).reshape(1, -1)
            
        except Exception as e:
            logging.error(f"Error construyendo características binarias: {e}")
            raise

class PredictionDecoder:
    """Decodificador de predicciones"""
    
    @staticmethod
    def decode_prediction(prediction, probabilities, preprocessor):
        """Decodificar predicción a diagnóstico legible"""
        try:
            if 'diagnosis_encoder' in preprocessor:
                diagnosis = preprocessor['diagnosis_encoder'].inverse_transform([prediction])[0]
            else:
                diagnosis = str(prediction)
            
            confidence = float(max(probabilities)) * 100
            
            return diagnosis, confidence
            
        except Exception as e:
            logging.error(f"Error decodificando predicción: {e}")
            return str(prediction), 0.0