import pickle
import os
import numpy as np
import re
from typing import Dict, List, Optional
from scipy.sparse import hstack, csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
import ssl
import logging

class PreprocesadorMedicoV11:
    def __init__(self, preprocesador_data):
        """Recrear preprocesador desde datos guardados"""
        
        print("🧠 Inicializando preprocesador médico v11 desde archivo...")
        
        # Cargar datos guardados
        self.medical_translations = preprocesador_data['medical_translations']
        self.embedding_dim = preprocesador_data['embedding_dim']
        self.stop_words_en = set(preprocesador_data['stop_words_en'])
        self.stop_words_es = set(preprocesador_data['stop_words_es'])
        
        # Inicializar NLTK (opcional - fallback si no está disponible)
        try:
            import nltk
            from nltk.corpus import stopwords
            from nltk.tokenize import word_tokenize
            from nltk.stem import WordNetLemmatizer
            
            # Configurar SSL
            try:
                _create_unverified_https_context = ssl._create_unverified_context
                ssl._create_default_https_context = _create_unverified_https_context
            except AttributeError:
                pass
            
            # Descargar recursos si es necesario
            nltk_resources = ['punkt', 'stopwords', 'wordnet', 'omw-1.4']
            for resource in nltk_resources:
                try:
                    nltk.download(resource, quiet=True)
                except:
                    pass
            
            self.lemmatizer = WordNetLemmatizer()
            print("✅ NLTK inicializado")
        except:
            self.lemmatizer = None
            print("⚠️ NLTK fallback activado")
        
        # Cargar Sentence-BERT (opcional - fallback si no está disponible)
        try:
            from sentence_transformers import SentenceTransformer
            print("🤖 Cargando Sentence-BERT...")
            self.sentence_model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ Sentence-BERT cargado")
        except Exception as e:
            print(f"⚠️ Sentence-BERT no disponible: {e}")
            self.sentence_model = None
    
    def detectar_idioma(self, texto: str) -> str:
        """Detectar idioma predominante del texto"""
        palabras_es = ['dolor', 'tengo', 'siento', 'mucho', 'cabeza', 'pecho', 'estómago', 'me', 'yo', 'muy', 'desde', 'hace']
        palabras_en = ['pain', 'have', 'feel', 'chest', 'head', 'stomach', 'back', 'breath', 'my', 'i', 'very', 'for', 'since']
        
        texto_lower = texto.lower()
        count_es = sum(1 for palabra in palabras_es if palabra in texto_lower)
        count_en = sum(1 for palabra in palabras_en if palabra in texto_lower)
        
        return 'spanish' if count_es > count_en else 'english'
    
    def aplicar_diccionario_medico(self, texto: str) -> str:
        """Aplicar diccionario médico para traducir términos"""
        texto_procesado = texto.lower().strip()
        
        for termino_es, termino_en in self.medical_translations.items():
            if termino_es in texto_procesado:
                texto_procesado = texto_procesado.replace(termino_es, f" {termino_en} ")
        
        texto_procesado = re.sub(r'\s+', ' ', texto_procesado).strip()
        return texto_procesado
    
    def limpiar_con_nltk(self, texto: str) -> str:
        """Limpiar texto usando NLTK con fallback"""
        try:
            if self.lemmatizer is None:
                return self._limpiar_basico(texto)
            
            import nltk
            from nltk.tokenize import word_tokenize
            
            tokens = word_tokenize(texto)
            clean_tokens = []
            
            for token in tokens:
                token_lower = token.lower()
                if (token_lower not in self.stop_words_en and 
                    token_lower not in self.stop_words_es and
                    token.isalpha() and 
                    len(token) > 2):
                    
                    lemmatized = self.lemmatizer.lemmatize(token_lower)
                    clean_tokens.append(lemmatized)
            
            return ' '.join(clean_tokens)
        except:
            return self._limpiar_basico(texto)
    
    def _limpiar_basico(self, texto: str) -> str:
        """Fallback de limpieza básica sin NLTK"""
        # Tokenizar básico
        texto = re.sub(r'[^\w\s]', ' ', texto)
        palabras = texto.lower().split()
        
        # Filtrar stopwords y palabras cortas
        palabras_filtradas = []
        for palabra in palabras:
            if (palabra not in self.stop_words_en and 
                palabra not in self.stop_words_es and
                len(palabra) > 2):
                palabras_filtradas.append(palabra)
        
        return ' '.join(palabras_filtradas)
    
    def generar_embeddings(self, texto: str) -> Optional[np.ndarray]:
        """Generar embeddings semánticos con Sentence-BERT con fallback"""
        if self.sentence_model is None:
            return np.zeros(384)  # Embedding vacío de 384 dimensiones
        
        try:
            embeddings = self.sentence_model.encode([texto])
            return embeddings[0]
        except Exception as e:
            print(f"❌ Error embeddings: {e}")
            return np.zeros(384)
    
    def procesar_texto_completo(self, texto: str) -> Dict:
        """Pipeline completo de procesamiento de texto médico"""
        idioma = self.detectar_idioma(texto)
        texto_traducido = self.aplicar_diccionario_medico(texto)
        texto_limpio = self.limpiar_con_nltk(texto_traducido)
        embeddings = self.generar_embeddings(texto_limpio)
        
        return {
            'texto_original': texto,
            'idioma_detectado': idioma,
            'texto_traducido': texto_traducido,
            'texto_limpio': texto_limpio,
            'embeddings': embeddings,
            'tiene_embeddings': embeddings is not None,
            'dimension_embeddings': len(embeddings) if embeddings is not None else 0
        }

class ModeloV11Loader:
    def __init__(self, model_path='models/v11_components/'):
        """Cargar modelo v11 desde componentes separados"""
        self.model_path = model_path
        self.modelo = None
        self.metadata = None
        self.preprocesador = None
        self._cargar_modelo()
    
    def _cargar_modelo(self):
        """Cargar todos los componentes del modelo v11"""
        try:
            print("🚀 Cargando modelo v11 desde componentes...")
            
            # 1. Cargar metadatos
            with open(f'{self.model_path}metadata.pkl', 'rb') as f:
                self.metadata = pickle.load(f)
            print(f"✅ Metadatos: v{self.metadata['version']} - {self.metadata['precision']:.4f} precisión")
            
            # 2. Cargar modelo XGBoost
            with open(f'{self.model_path}modelo_xgb.pkl', 'rb') as f:
                self.modelo_xgb = pickle.load(f)
            print("✅ Modelo XGBoost cargado")
            
            # 3. Cargar vectorizador TF-IDF
            with open(f'{self.model_path}tfidf_vectorizer.pkl', 'rb') as f:
                self.tfidf_vectorizer = pickle.load(f)
            print("✅ TF-IDF vectorizer cargado")
            
            # 4. Cargar encoders
            with open(f'{self.model_path}age_encoder.pkl', 'rb') as f:
                self.age_encoder = pickle.load(f)
            
            with open(f'{self.model_path}gender_encoder.pkl', 'rb') as f:
                self.gender_encoder = pickle.load(f)
            
            with open(f'{self.model_path}diagnosis_encoder.pkl', 'rb') as f:
                self.diagnosis_encoder = pickle.load(f)
            print("✅ Encoders cargados")
            
            # 5. Cargar datos del preprocesador
            with open(f'{self.model_path}preprocesador_data.pkl', 'rb') as f:
                preprocesador_data = pickle.load(f)
            
            # 6. Inicializar preprocesador
            self.preprocesador = PreprocesadorMedicoV11(preprocesador_data)
            print("✅ Preprocesador inicializado")
            
            print(f"🎯 Modelo v11 cargado exitosamente!")
            print(f"   📊 {self.metadata['num_clases']} clases de diagnóstico")
            print(f"   📅 Entrenado: {self.metadata['fecha']}")
            
        except Exception as e:
            print(f"❌ Error cargando modelo v11: {e}")
            self.modelo_xgb = None
            self.metadata = {"error": str(e)}
    
    def predecir(self, texto, edad="Unknown", genero="Unknown"):
        """Realizar predicción con modelo v11"""
        if self.modelo_xgb is None:
            return {'error': 'Modelo v11 no está disponible'}
        
        try:
            # 1. Procesar texto con preprocesador avanzado
            resultado_texto = self.preprocesador.procesar_texto_completo(texto)
            texto_limpio = resultado_texto['texto_limpio']
            
            # 2. Vectorizar con TF-IDF
            X_tfidf = self.tfidf_vectorizer.transform([texto_limpio])
            
            # 3. Obtener embeddings
            embeddings = resultado_texto['embeddings']
            if embeddings is None:
                embeddings = np.zeros(384)
            embeddings = embeddings.reshape(1, -1)
            X_embeddings = csr_matrix(embeddings)
            
            # 4. Codificar variables categóricas
            try:
                edad_enc = self.age_encoder.transform([edad])[0]
            except:
                edad_enc = 0
            
            try:
                genero_enc = self.gender_encoder.transform([genero])[0]
            except:
                genero_enc = 0
            
            X_categorical = csr_matrix(np.array([[edad_enc, genero_enc]]))
            
            # 5. Combinar todas las características
            X_final = hstack([X_tfidf, X_embeddings, X_categorical])
            
            # 6. Realizar predicción
            prediccion = self.modelo_xgb.predict(X_final)[0]
            probabilidades = self.modelo_xgb.predict_proba(X_final)[0]
            
            # 7. Obtener diagnosis y confianza
            diagnostico = self.diagnosis_encoder.classes_[prediccion]
            confianza = probabilidades[prediccion]
            
            # 8. Obtener top 3 predicciones
            top_indices = np.argsort(probabilidades)[::-1][:3]
            top_diagnosticos = []
            
            for i, idx in enumerate(top_indices):
                top_diagnosticos.append({
                    'diagnostico': self.diagnosis_encoder.classes_[idx],
                    'confianza': float(probabilidades[idx]),
                    'confianza_pct': f"{probabilidades[idx]*100:.1f}%"
                })
            
            return {
                'diagnostico_principal': diagnostico,
                'confianza': float(confianza),
                'confianza_pct': f"{confianza*100:.1f}%",
                'top_diagnosticos': top_diagnosticos,
                'idioma_detectado': resultado_texto['idioma_detectado'],
                'modelo_version': self.metadata['version'],
                'procesamiento': {
                    'texto_original': texto,
                    'texto_procesado': texto_limpio,
                    'embeddings_generados': resultado_texto['tiene_embeddings'],
                    'edad_procesada': edad,
                    'genero_procesado': genero
                }
            }
            
        except Exception as e:
            return {
                'error': f"Error en predicción: {str(e)}",
                'modelo_version': self.metadata['version'] if self.metadata else 'unknown'
            }
    
    def get_model_info(self):
        """Obtener información del modelo"""
        if self.metadata and 'error' not in self.metadata:
            return {
                'version': self.metadata['version'],
                'precision': self.metadata['precision'],
                'fecha_entrenamiento': self.metadata['fecha'],
                'num_clases': self.metadata['num_clases'],
                'embedding_dim': self.metadata['embedding_dim'],
                'estado': 'cargado',
                'clases_disponibles': list(self.metadata['clases'])[:10]  # Solo primeras 10
            }
        return {
            'version': 'v11',
            'estado': 'error',
            'error': self.metadata.get('error', 'Desconocido')
        }

# Instancia global del modelo v11
modelo_v11_global = None

def cargar_modelo_v11():
    """Cargar modelo v11 globalmente"""
    global modelo_v11_global
    if modelo_v11_global is None:
        modelo_v11_global = ModeloV11Loader()
    return modelo_v11_global

def predecir_v11(texto, edad="Unknown", genero="Unknown"):
    """Función de predicción rápida"""
    modelo = cargar_modelo_v11()
    return modelo.predecir(texto, edad, genero)