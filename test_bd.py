from src.database import db_manager

def test_database_setup():
    """Probar configuración completa de BD"""
    
    print("🧪 Probando conexión a base de datos...")
    
    # 1. Probar conexión
    result = db_manager.test_connection()
    print(f"Resultado conexión: {result}")
    
    if result['status'] == 'success':
        print("✅ Conexión exitosa!")
        
        # 2. Crear tablas
        print("\n📋 Creando tablas...")
        if db_manager.create_tables():
            print("✅ Tablas creadas exitosamente")
            
            # 3. Poblar con datos iniciales
            print("\n🌱 Poblando con datos iniciales...")
            if db_manager.seed_diagnoses_and_recommendations():
                print("✅ Datos iniciales insertados")
                
                # 4. Probar obtención de recomendaciones
                print("\n💡 Probando recomendaciones...")
                recommendations = db_manager.get_recommendations("Diabetes")
                print(f"Recomendaciones para Diabetes: {recommendations}")
                
                # 5. Probar log de predicción
                print("\n📝 Probando log de predicción...")
                success = db_manager.log_prediction(
                    symptoms="dolor de cabeza y fiebre",
                    diagnosis="Migraine",
                    confidence=85.5,
                    model_version="v8",
                    age_detected=30,
                    age_range="25-34",
                    gender="Female",
                    gender_origin="manual",
                    symptoms_processed="headache and fever"
                )
                print(f"Log predicción: {'✅' if success else '❌'}")
                
            else:
                print("❌ Error poblando datos")
        else:
            print("❌ Error creando tablas")
    else:
        print(f"❌ Error de conexión: {result['message']}")

if __name__ == "__main__":
    test_database_setup()