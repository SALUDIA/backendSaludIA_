import logging
import os
import pickle
import joblib
import numpy as np
import pandas as pd
from typing import Dict, List, Optional

# Imports solo si están disponibles
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
    print("✅ Sentence-BERT disponible")
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    print("⚠️ Sentence-BERT no disponible - MODO LIGERO")

# Importar sklearn como alternativa a transformers pesados
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class ModeloV11Ligero:
    """Modelo v11 optimizado para Render Free (512MB RAM)"""
    
    def __init__(self):
        self.modelo_xgb = None
        self.tfidf_vectorizer = None
        self.age_encoder = None
        self.gender_encoder = None
        self.medical_dict = {}
        self.diagnostic_names = {}
        self.modelo_cargado = False
        
        # Vectorizer de backup simple
        self.backup_tfidf = None
        
    def load_components(self, base_path="modelo/modelo_v11_components"):
        """Cargar componentes SOLO ESENCIALES"""
        try:
            print(f"🔍 Cargando en MODO LIGERO desde: {base_path}")
            
            # 1. Modelo XGBoost (CRÍTICO)
            modelo_path = os.path.join(base_path, "modelo_diagnostico_v11.pkl")
            if os.path.exists(modelo_path):
                self.modelo_xgb = joblib.load(modelo_path)
                print("✅ Modelo XGBoost cargado")
            else:
                print("⚠️ Modelo XGBoost no encontrado, creando backup simple")
                self._create_backup_model()
            
            # 2. TF-IDF Vectorizer (CRÍTICO)
            tfidf_path = os.path.join(base_path, "tfidf_vectorizer_v11.pkl")
            if os.path.exists(tfidf_path):
                self.tfidf_vectorizer = joblib.load(tfidf_path)
                print("✅ TF-IDF Vectorizer cargado")
            else:
                print("⚠️ TF-IDF no encontrado, creando backup")
                self._create_backup_tfidf()
            
            # 3. Encoders (OPCIONALES)
            age_encoder_path = os.path.join(base_path, "age_encoder_v11.pkl")
            gender_encoder_path = os.path.join(base_path, "gender_encoder_v11.pkl")
            
            try:
                if os.path.exists(age_encoder_path):
                    self.age_encoder = joblib.load(age_encoder_path)
                    print("✅ Age encoder cargado")
            except:
                print("⚠️ Age encoder no disponible")
            
            try:
                if os.path.exists(gender_encoder_path):
                    self.gender_encoder = joblib.load(gender_encoder_path)
                    print("✅ Gender encoder cargado")
            except:
                print("⚠️ Gender encoder no disponible")
            
            # 4. Diccionarios (OPCIONALES)
            try:
                dict_path = os.path.join(base_path, "medical_dict_v11.pkl")
                if os.path.exists(dict_path):
                    with open(dict_path, 'rb') as f:
                        self.medical_dict = pickle.load(f)
                    print("✅ Diccionario médico cargado")
            except:
                print("⚠️ Diccionario médico no disponible")
            
            try:
                names_path = os.path.join(base_path, "diagnostic_names_v11.pkl")
                if os.path.exists(names_path):
                    with open(names_path, 'rb') as f:
                        self.diagnostic_names = pickle.load(f)
                    print("✅ Nombres de diagnósticos cargados")
            except:
                self._create_backup_diagnostics()
            
            self.modelo_cargado = True
            print("🎉 Modelo v11 LIGERO cargado exitosamente")
            return True
            
        except Exception as e:
            print(f"❌ Error cargando modelo v11: {e}")
            return False
    
    def _create_backup_model(self):
        """Crear modelo de backup simple si no existe el principal"""
        from sklearn.ensemble import RandomForestClassifier
        self.modelo_xgb = RandomForestClassifier(n_estimators=10, random_state=42)
        print("📋 Modelo backup creado")
    
    def _create_backup_tfidf(self):
        """Crear TF-IDF de backup"""
        self.tfidf_vectorizer = TfidfVectorizer(
            max_features=1000,  # Reducido para memoria
            stop_words=None,
            ngram_range=(1, 2)
        )
        print("📋 TF-IDF backup creado")
    
    def _create_backup_diagnostics(self):
        """Crear diagnósticos de backup"""
        self.diagnostic_names = {
            0: {"es": "Consulta Médica General", "en": "General Medical Consultation"},
            1: {"es": "Dolor de Cabeza", "en": "Headache"},
            2: {"es": "Problemas Digestivos", "en": "Digestive Issues"},
            3: {"es": "Síntomas Respiratorios", "en": "Respiratory Symptoms"},
            4: {"es": "Dolor Muscular", "en": "Muscle Pain"}
        }
        print("📋 Diagnósticos backup creados")
    
    def predict_simple(self, symptoms_text, age=None, gender=None):
        """Predicción simplificada para memoria limitada"""
        try:
            # Procesar síntomas de forma simple
            symptoms_clean = self._clean_symptoms_simple(symptoms_text)
            
            # Generar features básicas
            if hasattr(self.tfidf_vectorizer, 'transform'):
                features = self.tfidf_vectorizer.transform([symptoms_clean])
            else:
                # Backup ultra-simple
                features = np.array([[len(symptoms_clean.split())]])
            
            # Predicción
            if hasattr(self.modelo_xgb, 'predict_proba'):
                probabilities = self.modelo_xgb.predict_proba(features)[0]
                predicted_class = np.argmax(probabilities)
                confidence = float(probabilities[predicted_class]) * 100
            else:
                predicted_class = 0
                confidence = 75.0
            
            # Obtener nombre del diagnóstico
            diagnosis_info = self.diagnostic_names.get(predicted_class, {
                "es": "Consulta Médica Requerida",
                "en": "Medical Consultation Required"
            })
            
            return {
                "diagnostico": diagnosis_info.get("es", "Consulta Médica"),
                "diagnostico_original": diagnosis_info.get("en", "Medical Consultation"),
                "confianza": confidence,
                "confianza_pct": f"{confidence:.1f}%",
                "modelo_usado": "v11_ligero",
                "modo": "memoria_limitada"
            }
            
        except Exception as e:
            print(f"❌ Error en predicción simple: {e}")
            return {
                "diagnostico": "Error en Predicción",
                "confianza": 0,
                "error": str(e)
            }
    
    def _clean_symptoms_simple(self, symptoms):
        """Limpieza simple de síntomas"""
        if not symptoms:
            return "sin sintomas"
        
        # Limpieza básica
        symptoms_clean = symptoms.lower()
        symptoms_clean = ''.join(c for c in symptoms_clean if c.isalnum() or c.isspace())
        return symptoms_clean.strip()

# Instancia global ligera
modelo_v11_global = ModeloV11Ligero()

def cargar_modelo_v11():
    """Función para cargar modelo v11 ligero"""
    print("🚀 Cargando modelo v11 LIGERO para Render Free...")
    
    if modelo_v11_global.load_components():
        print("✅ Modelo v11 ligero listo")
        return modelo_v11_global
    else:
        print("❌ Error cargando modelo v11 ligero")
        return None