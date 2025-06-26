from googletrans import Translator
import re
import logging

class TranslatorManager:
    """Gestor de traducción y categorización automática"""
    
    def __init__(self):
        self.translator = Translator()
        
        # Mapeo de rangos de edad
        self.age_ranges = {
            (0, 12): "0-12",
            (13, 17): "13-17", 
            (18, 24): "18-24",
            (25, 34): "25-34",
            (35, 44): "35-44",
            (45, 54): "45-54",
            (55, 64): "55-64",
            (65, 120): "65+"
        }
        
        # Palabras clave para detectar género en síntomas
        self.gender_keywords = {
            'female': [
                'embarazo', 'embarazada', 'menstruación', 'regla', 'período',
                'ovarios', 'útero', 'vaginal', 'menstrual', 'parto',
                'lactancia', 'menopausia', 'embarazo', 'gestación'
            ],
            'male': [
                'próstata', 'testículos', 'pene', 'esperma', 'eyaculación',
                'erección', 'testicular', 'prostático'
            ]
        }
    
    def translate_to_english(self, text):
        """Traducir texto al inglés"""
        try:
            if not text or text.strip() == '':
                return "patient presents with general symptoms"
            
            # Detectar si ya está en inglés
            detected = self.translator.detect(text)
            if detected.lang == 'en':
                return text
            
            # Traducir al inglés
            translated = self.translator.translate(text, src='es', dest='en')
            return translated.text
            
        except Exception as e:
            logging.error(f"Error en traducción a inglés: {e}")
            return f"patient experiences {text}"  # Fallback simple
    
    def translate_to_spanish(self, text):
        """Traducir texto al español"""
        try:
            if not text:
                return "Síntomas generales"
            
            # Detectar si ya está en español
            detected = self.translator.detect(text)
            if detected.lang == 'es':
                return text
            
            # Traducir al español
            translated = self.translator.translate(text, src='en', dest='es')
            return translated.text
            
        except Exception as e:
            logging.error(f"Error en traducción a español: {e}")
            # Mapeo manual básico como fallback
            basic_translations = {
                'Diabetes': 'Diabetes',
                'Hypertension': 'Hipertensión',
                'Migraine': 'Migraña',
                'Asthma': 'Asma',
                'Gastroenteritis': 'Gastroenteritis',
                'Bronchitis': 'Bronquitis',
                'Arthritis': 'Artritis',
                'Allergy': 'Alergia',
                'Pneumonia': 'Neumonía',
                'Urinary tract infection': 'Infección del tracto urinario'
            }
            return basic_translations.get(text, text)
    
    def categorize_age(self, age):
        """Categorizar edad en rango"""
        try:
            age_num = int(age)
            for (min_age, max_age), range_str in self.age_ranges.items():
                if min_age <= age_num <= max_age:
                    return range_str
            return "25-34"  # Default
        except:
            return "25-34"  # Default si no se puede parsear
    
    def detect_gender(self, symptoms_text):
        """Detectar género basado en síntomas"""
        symptoms_lower = symptoms_text.lower()
        
        # Buscar palabras clave femeninas
        female_score = sum(1 for keyword in self.gender_keywords['female'] 
                          if keyword in symptoms_lower)
        
        # Buscar palabras clave masculinas  
        male_score = sum(1 for keyword in self.gender_keywords['male']
                        if keyword in symptoms_lower)
        
        if female_score > male_score:
            return "Female"
        elif male_score > female_score:
            return "Male"
        else:
            return "Unknown"  # No se puede determinar
    
    def extract_age_from_text(self, text):
        """Extraer edad del texto si se menciona"""
        age_patterns = [
            r'(\d+)\s*años?',
            r'edad\s*(\d+)',
            r'tengo\s*(\d+)',
            r'soy\s*de\s*(\d+)',
            r'(\d+)\s*years?',
            r'age\s*(\d+)'
        ]
        
        for pattern in age_patterns:
            match = re.search(pattern, text.lower())
            if match:
                age = int(match.group(1))
                if 0 <= age <= 120:  # Validar rango razonable
                    return age
        
        return None

# Instancia global
translator_manager = TranslatorManager()