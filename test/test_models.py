import os
import joblib
import pickle
import traceback

def check_model_integrity():
    """Verificar integridad completa del modelo v8"""
    
    print("🔍 DIAGNÓSTICO COMPLETO DEL MODELO V8")
    print("="*60)
    
    # Rutas de archivos
    model_path = '../../Backend/models/modelo_diagnostico_v8_reentrenado.pkl'
    preprocessor_path = '../../Backend/models/preprocesadores_v8_reentrenado.pkl'
    
    # 1. Verificar existencia y tamaño
    print("📁 VERIFICANDO ARCHIVOS:")
    for name, path in [("Modelo V8", model_path), ("Preprocesadores V8", preprocessor_path)]:
        if os.path.exists(path):
            size = os.path.getsize(path)
            size_mb = size / (1024 * 1024)
            print(f"   ✅ {name}: {size_mb:.2f} MB")
            
            # Verificar si el archivo está vacío o muy pequeño
            if size < 1024:  # Menos de 1KB
                print(f"   ⚠️ ADVERTENCIA: Archivo muy pequeño ({size} bytes)")
            elif size < 10240:  # Menos de 10KB
                print(f"   ⚠️ ADVERTENCIA: Archivo sospechosamente pequeño")
        else:
            print(f"   ❌ {name}: NO ENCONTRADO")
            return False
    
    # 2. Probar carga con joblib
    print(f"\n🔧 PROBANDO CARGA CON JOBLIB:")
    
    try:
        print(f"   📖 Cargando modelo...")
        model = joblib.load(model_path)
        print(f"   ✅ Modelo cargado exitosamente")
        print(f"   🔍 Tipo: {type(model)}")
        
        # Verificar si tiene métodos necesarios
        has_predict = hasattr(model, 'predict')
        has_predict_proba = hasattr(model, 'predict_proba')
        print(f"   📋 Métodos disponibles:")
        print(f"      - predict: {'✅' if has_predict else '❌'}")
        print(f"      - predict_proba: {'✅' if has_predict_proba else '❌'}")
        
    except Exception as e:
        print(f"   ❌ Error cargando modelo: {e}")
        print(f"   📋 Detalles del error:")
        traceback.print_exc()
        
        # Intentar con pickle directo
        print(f"\n   🔄 Intentando con pickle directo...")
        try:
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            print(f"   ✅ Cargado con pickle directo")
        except Exception as e2:
            print(f"   ❌ También falló con pickle: {e2}")
            return False
    
    try:
        print(f"\n   📖 Cargando preprocesadores...")
        preprocessors = joblib.load(preprocessor_path)
        print(f"   ✅ Preprocesadores cargados exitosamente")
        print(f"   🔍 Tipo: {type(preprocessors)}")
        
        # Verificar estructura
        if isinstance(preprocessors, dict):
            print(f"   📋 Claves encontradas: {list(preprocessors.keys())}")
            
            for key, value in preprocessors.items():
                print(f"      - {key}: {type(value)}")
        else:
            print(f"   ⚠️ No es un diccionario, es: {type(preprocessors)}")
            
    except Exception as e:
        print(f"   ❌ Error cargando preprocesadores: {e}")
        traceback.print_exc()
        return False
    
    # 3. Probar predicción de prueba
    print(f"\n🧪 PROBANDO PREDICCIÓN DE PRUEBA:")
    
    try:
        # Obtener vectorizer
        if isinstance(preprocessors, dict):
            vectorizer = preprocessors.get('vectorizer')
            label_encoder = preprocessors.get('label_encoder')
        else:
            vectorizer = preprocessors
            label_encoder = None
        
        if not vectorizer:
            print(f"   ❌ No se encontró vectorizer")
            return False
        
        print(f"   🔍 Vectorizer tipo: {type(vectorizer)}")
        
        # Texto de prueba
        test_text = "dolor de cabeza y fiebre"
        print(f"   📝 Texto de prueba: '{test_text}'")
        
        # Vectorizar
        vector = vectorizer.transform([test_text])
        print(f"   ✅ Vectorización exitosa: {vector.shape}")
        
        # Predicción
        prediction = model.predict(vector)
        print(f"   ✅ Predicción exitosa: {prediction}")
        
        # Probabilidades
        if hasattr(model, 'predict_proba'):
            probabilities = model.predict_proba(vector)
            print(f"   ✅ Probabilidades: {probabilities}")
        
        # Decodificar si hay label_encoder
        if label_encoder:
            try:
                decoded = label_encoder.inverse_transform(prediction)
                print(f"   ✅ Decodificación: {decoded}")
            except Exception as e:
                print(f"   ⚠️ Error decodificando: {e}")
        
        print(f"\n🎉 ¡MODELO V8 FUNCIONA CORRECTAMENTE!")
        return True
        
    except Exception as e:
        print(f"   ❌ Error en predicción de prueba: {e}")
        traceback.print_exc()
        return False

def fix_model_loading():
    """Intentar arreglar problemas comunes de carga"""
    
    print(f"\n🔧 INTENTANDO ARREGLOS AUTOMÁTICOS:")
    
    # Verificar versiones de librerías
    try:
        import sklearn
        import joblib
        print(f"   📦 Scikit-learn: {sklearn.__version__}")
        print(f"   📦 Joblib: {joblib.__version__}")
        
        # Verificar compatibilidad
        sklearn_version = tuple(map(int, sklearn.__version__.split('.')[:2]))
        
        if sklearn_version < (1, 0):
            print(f"   ⚠️ Scikit-learn muy antiguo, puede causar problemas")
        elif sklearn_version > (1, 3):
            print(f"   ⚠️ Scikit-learn muy nuevo, puede haber incompatibilidad")
        else:
            print(f"   ✅ Versión de scikit-learn compatible")
            
    except Exception as e:
        print(f"   ❌ Error verificando versiones: {e}")
    
    # Sugerir regeneración si es necesario
    print(f"\n💡 SUGERENCIAS:")
    print(f"   1. Si el modelo falla constantemente, regenerarlo")
    print(f"   2. Verificar que se entrenó con la misma versión de scikit-learn")
    print(f"   3. Usar pickle en lugar de joblib si persiste el problema")

if __name__ == '__main__':
    success = check_model_integrity()
    
    if not success:
        fix_model_loading()
        
    print(f"\n{'='*60}")
    if success:
        print(f"✅ MODELO V8 ESTÁ FUNCIONANDO CORRECTAMENTE")
        print(f"🚀 Puedes ejecutar: python app.py")
    else:
        print(f"❌ MODELO V8 TIENE PROBLEMAS")
        print(f"🔧 Revisar sugerencias arriba")