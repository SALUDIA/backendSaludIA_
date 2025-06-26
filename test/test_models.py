import os
import sys
sys.path.append('..')

from src.predictor import model_manager

def test_models_loading():
    """Test básico de carga de modelos"""
    print("🧪 Probando carga de modelos...")
    
    available = model_manager.get_available_models()
    print(f"Modelos disponibles: {available}")
    
    assert len(available) > 0, "No se cargó ningún modelo"
    print("✅ Al menos un modelo está disponible")

def test_text_prediction():
    """Test de predicción con texto"""
    if 'v8' in model_manager.models:
        result = model_manager.predict_text("dolor de cabeza y fiebre", 'v8')
        assert 'diagnosis' in result, "Predicción de texto falló"
        print("✅ Predicción de texto funciona")

def test_binary_prediction():
    """Test de predicción binaria"""
    if 'v9' in model_manager.models:
        symptoms = [1, 0, 1, 0] * 33  # 132 síntomas binarios
        result = model_manager.predict_binary(symptoms, 'v9')
        assert 'diagnosis' in result, "Predicción binaria falló"
        print("✅ Predicción binaria funciona")

if __name__ == '__main__':
    test_models_loading()
    test_text_prediction()
    test_binary_prediction()
    print("🎉 Todos los tests pasaron")