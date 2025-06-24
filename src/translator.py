from googletrans import Translator
import time
import os

class SymptomTranslator:
    """Traductor de síntomas usando Google Translate"""
    
    def __init__(self):
        self.translator = Translator()
        self.timeout = int(os.getenv('TRANSLATOR_TIMEOUT', 10))
        
        # Cache básico para evitar traducciones repetidas
        self.cache = {}
    
    def detect_and_translate(self, text):
        """
        Detectar idioma y traducir al inglés si es necesario
        
        Args:
            text (str): Texto a traducir
            
        Returns:
            dict: {
                'original_text': str,
                'translated_text': str,
                'detected_language': str,
                'confidence': float,
                'was_translated': bool
            }
        """
        try:
            # Limpiar texto
            text = str(text).strip()
            
            if not text:
                return {
                    'original_text': text,
                    'translated_text': text,
                    'detected_language': 'unknown',
                    'confidence': 0.0,
                    'was_translated': False,
                    'error': 'Texto vacío'
                }
            
            # Verificar cache
            cache_key = text.lower()
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # Detectar idioma
            detected = self.translator.detect(text)
            detected_lang = detected.lang
            confidence = detected.confidence
            
            # Si ya está en inglés, no traducir
            if detected_lang == 'en':
                result = {
                    'original_text': text,
                    'translated_text': text,
                    'detected_language': detected_lang,
                    'confidence': confidence,
                    'was_translated': False
                }
            else:
                # Traducir al inglés
                translated = self.translator.translate(text, dest='en', src=detected_lang)
                result = {
                    'original_text': text,
                    'translated_text': translated.text,
                    'detected_language': detected_lang,
                    'confidence': confidence,
                    'was_translated': True
                }
            
            # Guardar en cache
            self.cache[cache_key] = result
            
            return result
            
        except Exception as e:
            # En caso de error, devolver texto original
            return {
                'original_text': text,
                'translated_text': text,
                'detected_language': 'unknown',
                'confidence': 0.0,
                'was_translated': False,
                'error': str(e)
            }
    
    def translate_to_spanish(self, text, source_lang='en'):
        """
        Traducir texto al español
        
        Args:
            text (str): Texto a traducir
            source_lang (str): Idioma fuente (por defecto 'en')
            
        Returns:
            str: Texto traducido al español
        """
        try:
            if not text:
                return text
            
            # Cache para traducciones al español
            cache_key = f"{text}_{source_lang}_es"
            if cache_key in self.cache:
                return self.cache[cache_key]
            
            # Traducir
            translated = self.translator.translate(text, dest='es', src=source_lang)
            result = translated.text
            
            # Guardar en cache
            self.cache[cache_key] = result
            
            return result
            
        except Exception as e:
            print(f"⚠️ Error traduciendo '{text}': {e}")
            return text
    
    def clear_cache(self):
        """Limpiar cache de traducciones"""
        self.cache.clear()
    
    def get_cache_stats(self):
        """Obtener estadísticas del cache"""
        return {
            'total_cached': len(self.cache),
            'cache_keys': list(self.cache.keys())[:10]  # Solo primeras 10
        }