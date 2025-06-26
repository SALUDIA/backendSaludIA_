from deep_translator import GoogleTranslator
import logging
import re

class TranslatorManager:
    """Gestor de traducción usando deep-translator (compatible con Python 3.13)"""
    
    def __init__(self):
        self.translator_es_to_en = GoogleTranslator(source='es', target='en')
        self.translator_en_to_es = GoogleTranslator(source='en', target='es')
        print("✅ Translator Manager inicializado con deep-translator")
    
    def translate_to_english(self, text_spanish):
        """Traducir texto de español a inglés"""
        try:
            if not text_spanish or not isinstance(text_spanish, str):
                return ""
            
            # Limpiar el texto
            text_cleaned = text_spanish.strip()
            if len(text_cleaned) == 0:
                return ""
            
            # Traducir
            result = self.translator_es_to_en.translate(text_cleaned)
            
            if result:
                print(f"🔄 Traducido ES→EN: '{text_spanish[:50]}...' → '{result[:50]}...'")
                return result
            else:
                print(f"⚠️ No se pudo traducir: {text_spanish}")
                return text_spanish  # Retornar original si falla
                
        except Exception as e:
            logging.error(f"Error traduciendo a inglés: {e}")
            print(f"❌ Error traduciendo: {e}")
            return text_spanish  # Retornar original si hay error
    
    def translate_to_spanish(self, text_english):
        """Traducir texto de inglés a español"""
        try:
            if not text_english or not isinstance(text_english, str):
                return ""
            
            # Limpiar el texto
            text_cleaned = text_english.strip()
            if len(text_cleaned) == 0:
                return ""
            
            # Traducir
            result = self.translator_en_to_es.translate(text_cleaned)
            
            if result:
                print(f"🔄 Traducido EN→ES: '{text_english[:50]}...' → '{result[:50]}...'")
                return result
            else:
                print(f"⚠️ No se pudo traducir: {text_english}")
                return text_english  # Retornar original si falla
                
        except Exception as e:
            logging.error(f"Error traduciendo a español: {e}")
            print(f"❌ Error traduciendo: {e}")
            return text_english  # Retornar original si hay error
    
    def extract_age_from_text(self, text):
        """Extraer edad del texto en español"""
        try:
            # Patrones para detectar edad
            age_patterns = [
                r'tengo (\d+) años',
                r'(\d+) años',
                r'edad (\d+)',
                r'soy de (\d+)',
                r'(\d+) años de edad'
            ]
            
            for pattern in age_patterns:
                match = re.search(pattern, text.lower())
                if match:
                    age = int(match.group(1))
                    if 1 <= age <= 120:  # Validar rango razonable
                        print(f"📅 Edad extraída: {age} años")
                        return age
            
            return None
            
        except Exception as e:
            logging.error(f"Error extrayendo edad: {e}")
            return None
    
    def categorize_age(self, age):
        """Categorizar edad en rangos"""
        try:
            if age < 18:
                return "0-17"
            elif age < 25:
                return "18-24"
            elif age < 35:
                return "25-34"
            elif age < 45:
                return "35-44"
            elif age < 55:
                return "45-54"
            elif age < 65:
                return "55-64"
            else:
                return "65+"
        except:
            return "25-34"  # Categoría por defecto
    
    def detect_gender(self, text):
        """Detectar género desde el texto en español"""
        try:
            text_lower = text.lower()
            
            # Patrones para detectar género femenino
            female_patterns = [
                r'\bestoy embarazada\b',
                r'\bmenstruación\b',
                r'\bmenstrual\b',
                r'\bovarios\b',
                r'\bútero\b',
                r'\bmenopausia\b',
                r'\bginecológico\b',
                r'\bsoy mujer\b',
                r'\bsoy femenina\b',
                r'\bestoy lactando\b'
            ]
            
            # Patrones para detectar género masculino
            male_patterns = [
                r'\bpróstata\b',
                r'\btestículos\b',
                r'\bsoy hombre\b',
                r'\bsoy masculino\b',
                r'\bandrológico\b'
            ]
            
            # Buscar patrones femeninos
            for pattern in female_patterns:
                if re.search(pattern, text_lower):
                    print(f"👩 Género detectado: Female (patrón: {pattern})")
                    return "Female"
            
            # Buscar patrones masculinos
            for pattern in male_patterns:
                if re.search(pattern, text_lower):
                    print(f"👨 Género detectado: Male (patrón: {pattern})")
                    return "Male"
            
            print("❓ Género no detectado, usando Unknown")
            return "Unknown"
            
        except Exception as e:
            logging.error(f"Error detectando género: {e}")
            return "Unknown"

# Instancia global
translator_manager = TranslatorManager()