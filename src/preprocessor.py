import re
import string
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Descargar recursos NLTK si no están disponibles
def download_nltk_data():
    """Descargar recursos necesarios de NLTK"""
    try:
        word_tokenize("test")
        stopwords.words('english')
        WordNetLemmatizer().lemmatize("test")
    except (LookupError, OSError):
        print("📦 Descargando recursos de NLTK...")
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('wordnet', quiet=True)
        nltk.download('punkt_tab', quiet=True)
        print("✅ Recursos NLTK descargados")

# Descargar al importar el módulo
download_nltk_data()

def preprocess_text_advanced(text):
    """
    Preprocesamiento avanzado de texto médico
    Compatible con el modelo v8
    """
    if pd.isna(text) or text is None or text == '':
        return ''
    
    # Convertir a string y minúsculas
    text = str(text).lower()
    
    # Remover patrones médicos específicos pero preservar información importante
    text = re.sub(r'\b(patient|enrollee|reviewer|medical|treatment)\b', '', text)
    text = re.sub(r'\b\d+[-/]\d+[-/]\d+\b', '', text)  # Fechas
    text = re.sub(r'\b\d{2,4}\b', '', text)  # Años/números grandes
    
    # Preservar términos médicos importantes
    medical_terms = [
        'hypertension', 'diabetes', 'cardiac', 'hepatitis', 'autism', 
        'depression', 'anxiety', 'therapy', 'surgery', 'medication',
        'fever', 'cough', 'fatigue', 'breathing', 'cholesterol',
        'headache', 'nausea', 'vomiting', 'diarrhea', 'constipation',
        'asthma', 'pneumonia', 'bronchitis', 'influenza', 'migraine',
        'eczema', 'dermatitis', 'arthritis', 'osteoporosis', 'anemia'
    ]
    
    # Remover puntuación
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Tokenización
    tokens = word_tokenize(text)
    
    # Lemmatización y filtrado
    lemmatizer = WordNetLemmatizer()
    stop_words = set(stopwords.words('english'))
    
    # Filtrar tokens manteniendo términos médicos importantes
    tokens = [
        lemmatizer.lemmatize(word) for word in tokens 
        if (word not in stop_words and len(word) > 2) or word in medical_terms
    ]
    
    return ' '.join(tokens)

def validate_input(symptoms, age_range, gender):
    """
    Validar entrada del usuario
    """
    errors = []
    
    # Validar síntomas
    if not symptoms or len(symptoms.strip()) < 5:
        errors.append("Los síntomas deben tener al menos 5 caracteres")
    
    # Validar rango de edad
    valid_ages = ['0-10', '11_20', '21-30', '31-40', '41-50', '51-64', '65+', '0-20', '51-60', '61-70', '71+']
    if age_range not in valid_ages:
        errors.append(f"Rango de edad inválido. Opciones válidas: {valid_ages}")
    
    # Validar género
    valid_genders = ['Male', 'Female']
    if gender not in valid_genders:
        errors.append(f"Género inválido. Opciones válidas: {valid_genders}")
    
    return errors

def format_symptoms_for_model(symptoms):
    """
    Formatear síntomas para el modelo
    """
    # Si los síntomas no están en formato médico, convertirlos
    if not symptoms.lower().startswith('patient'):
        formatted = f"Patient presents with {symptoms.lower()}"
    else:
        formatted = symptoms
    
    return formatted