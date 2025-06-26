from src.database import db_manager
import mysql.connector
from mysql.connector import Error

def insert_all_diseases_and_recommendations():
    """Insertar todas las enfermedades con sus recomendaciones"""
    
    print("🗄️ === INSERTANDO TODAS LAS ENFERMEDADES Y RECOMENDACIONES ===")
    
    if not db_manager.connect():
        print("❌ No se pudo conectar a la base de datos")
        return False
    
    try:
        cursor = db_manager.connection.cursor()
        
        # PASO 1: Limpiar datos existentes (opcional)
        print("🧹 Limpiando datos existentes...")
        cursor.execute("DELETE FROM recommendations WHERE id > 0")
        cursor.execute("DELETE FROM diagnoses WHERE id > 0")
        cursor.execute("ALTER TABLE diagnoses AUTO_INCREMENT = 1")
        cursor.execute("ALTER TABLE recommendations AUTO_INCREMENT = 1")
        
        # PASO 2: Definir TODAS las enfermedades y recomendaciones
        all_diseases_data = {
            # Enfermedades cardiovasculares
            "Hypertension": {
                "name_es": "Hipertensión",
                "description": "Presión arterial elevada de forma persistente",
                "recommendations": [
                    ("Reduce el consumo de sal en tu dieta", "diet", 1),
                    ("Controla tu presión arterial regularmente", "monitoring", 2),
                    ("Evita el estrés y practica técnicas de relajación", "lifestyle", 3),
                    ("Realiza ejercicio cardiovascular moderado", "exercise", 4),
                    ("Mantén un peso saludable", "lifestyle", 5)
                ]
            },
            "Heart disease": {
                "name_es": "Enfermedad cardíaca",
                "description": "Trastornos que afectan al corazón",
                "recommendations": [
                    ("Sigue una dieta baja en grasas saturadas", "diet", 1),
                    ("Realiza ejercicio bajo supervisión médica", "exercise", 2),
                    ("No fumes y evita el humo de segunda mano", "lifestyle", 3),
                    ("Controla el colesterol regularmente", "monitoring", 4)
                ]
            },
            "Cardiovascular": {
                "name_es": "Cardiovascular",
                "description": "Trastornos del corazón y vasos sanguíneos",
                "recommendations": [
                    ("Mantén una dieta rica en frutas y verduras", "diet", 1),
                    ("Limita el consumo de alcohol", "lifestyle", 2),
                    ("Controla tu peso corporal", "lifestyle", 3),
                    ("Realiza chequeos cardíacos regulares", "monitoring", 4)
                ]
            },
            
            # Enfermedades respiratorias
            "Asthma": {
                "name_es": "Asma",
                "description": "Enfermedad respiratoria crónica",
                "recommendations": [
                    ("Evita los desencadenantes conocidos", "prevention", 1),
                    ("Mantén tu inhalador siempre disponible", "medical", 2),
                    ("Realiza ejercicios de respiración", "lifestyle", 3),
                    ("Mantén tu hogar libre de alérgenos", "environment", 4)
                ]
            },
            "Bronchitis": {
                "name_es": "Bronquitis",
                "description": "Inflamación de los bronquios",
                "recommendations": [
                    ("Descansa lo suficiente para ayudar a tu recuperación", "rest", 1),
                    ("Bebe mucha agua para aflojar las secreciones", "hydration", 2),
                    ("Evita el humo del cigarrillo y otros irritantes", "prevention", 3),
                    ("Usa un humidificador en tu habitación", "environment", 4)
                ]
            },
            "Pneumonia": {
                "name_es": "Neumonía",
                "description": "Infección pulmonar",
                "recommendations": [
                    ("Descansa completamente y evita esfuerzos físicos", "rest", 1),
                    ("Mantente bien hidratado", "hydration", 2),
                    ("Busca atención médica inmediata si empeoran los síntomas", "medical", 3),
                    ("Toma todos los medicamentos según prescripción", "medical", 4)
                ]
            },
            "Respiratory": {
                "name_es": "Respiratorio",
                "description": "Trastornos del sistema respiratorio",
                "recommendations": [
                    ("Evita la exposición a contaminantes del aire", "prevention", 1),
                    ("Practica técnicas de respiración profunda", "lifestyle", 2),
                    ("Mantén una buena postura para facilitar la respiración", "lifestyle", 3),
                    ("Vacúnate contra enfermedades respiratorias", "prevention", 4)
                ]
            },
            
            # Enfermedades gastrointestinales
            "Gastroenteritis": {
                "name_es": "Gastroenteritis",
                "description": "Inflamación del tracto gastrointestinal",
                "recommendations": [
                    ("Mantente hidratado bebiendo líquidos claros", "hydration", 1),
                    ("Come alimentos blandos y fáciles de digerir", "diet", 2),
                    ("Evita lácteos y alimentos grasos temporalmente", "diet", 3),
                    ("Descansa hasta que mejoren los síntomas", "rest", 4)
                ]
            },
            "Gastrointestinal": {
                "name_es": "Gastrointestinal",
                "description": "Trastornos del sistema digestivo",
                "recommendations": [
                    ("Mantén una dieta equilibrada y regular", "diet", 1),
                    ("Evita alimentos que te causen malestar", "diet", 2),
                    ("Come porciones pequeñas y frecuentes", "diet", 3),
                    ("Reduce el estrés que puede afectar la digestión", "lifestyle", 4)
                ]
            },
            
            # Enfermedades neurológicas
            "Migraine": {
                "name_es": "Migraña",
                "description": "Tipo de dolor de cabeza recurrente e intenso",
                "recommendations": [
                    ("Identifica y evita los desencadenantes de dolor", "prevention", 1),
                    ("Mantén horarios regulares de sueño", "lifestyle", 2),
                    ("Considera técnicas de manejo del estrés", "lifestyle", 3),
                    ("Mantén un diario de dolores de cabeza", "monitoring", 4)
                ]
            },
            "Central Nervous System/ Neuromuscular": {
                "name_es": "Sistema Nervioso Central/Neuromuscular",
                "description": "Trastornos del sistema nervioso y muscular",
                "recommendations": [
                    ("Mantén un estilo de vida activo y saludable", "lifestyle", 1),
                    ("Evita factores que puedan empeorar los síntomas", "prevention", 2),
                    ("Busca evaluación neurológica especializada", "medical", 3),
                    ("Considera terapias de rehabilitación física", "treatment", 4),
                    ("Mantén una rutina de ejercicios adaptada", "exercise", 5)
                ]
            },
            
            # Enfermedades musculoesqueléticas
            "Arthritis": {
                "name_es": "Artritis",
                "description": "Inflamación de las articulaciones",
                "recommendations": [
                    ("Mantén un peso saludable para reducir presión en articulaciones", "lifestyle", 1),
                    ("Realiza ejercicios de bajo impacto regularmente", "exercise", 2),
                    ("Aplica calor o frío según te resulte más cómodo", "treatment", 3),
                    ("Evita actividades que sobrecarguen las articulaciones", "prevention", 4)
                ]
            },
            "Musculoskeletal": {
                "name_es": "Musculoesquelético",
                "description": "Trastornos de músculos y huesos",
                "recommendations": [
                    ("Mantén una postura correcta", "lifestyle", 1),
                    ("Realiza ejercicios de fortalecimiento", "exercise", 2),
                    ("Aplica terapias de calor o frío según sea necesario", "treatment", 3),
                    ("Evita movimientos bruscos o repetitivos", "prevention", 4)
                ]
            },
            
            # Enfermedades metabólicas
            "Diabetes": {
                "name_es": "Diabetes",
                "description": "Enfermedad metabólica caracterizada por niveles altos de glucosa",
                "recommendations": [
                    ("Controla regularmente tus niveles de glucosa", "monitoring", 1),
                    ("Mantén una dieta balanceada baja en azúcares", "diet", 2),
                    ("Realiza ejercicio moderado regularmente", "exercise", 3),
                    ("Toma tus medicamentos según prescripción", "medical", 4),
                    ("Mantén un peso corporal saludable", "lifestyle", 5)
                ]
            },
            
            # Alergias e inmunológicas
            "Allergy": {
                "name_es": "Alergia",
                "description": "Reacción del sistema inmunitario a sustancias",
                "recommendations": [
                    ("Identifica y evita los alérgenos que te afectan", "prevention", 1),
                    ("Mantén tu hogar libre de polvo y ácaros", "environment", 2),
                    ("Considera llevar antihistamínicos cuando sea necesario", "medical", 3),
                    ("Usa ropa y ropa de cama hipoalergénica", "lifestyle", 4)
                ]
            },
            
            # Infecciones
            "Urinary tract infection": {
                "name_es": "Infección del tracto urinario",
                "description": "Infección en el sistema urinario",
                "recommendations": [
                    ("Bebe mucha agua para ayudar a eliminar bacterias", "hydration", 1),
                    ("No retengas la orina, ve al baño cuando sientas la necesidad", "lifestyle", 2),
                    ("Evita irritantes como cafeína y alcohol", "diet", 3),
                    ("Mantén una buena higiene personal", "hygiene", 4)
                ]
            },
            "Infection": {
                "name_es": "Infección",
                "description": "Invasión de microorganismos patógenos",
                "recommendations": [
                    ("Mantén una buena higiene personal", "hygiene", 1),
                    ("Toma antibióticos solo según prescripción médica", "medical", 2),
                    ("Descansa lo suficiente para fortalecer el sistema inmune", "rest", 3),
                    ("Evita el contacto cercano con personas enfermas", "prevention", 4)
                ]
            },
            
            # Dermatológicas
            "Skin": {
                "name_es": "Piel",
                "description": "Trastornos de la piel",
                "recommendations": [
                    ("Mantén la piel limpia e hidratada", "hygiene", 1),
                    ("Evita la exposición excesiva al sol", "prevention", 2),
                    ("Usa protector solar diariamente", "prevention", 3),
                    ("Evita rascarte las áreas afectadas", "lifestyle", 4)
                ]
            },
            
            # Salud mental
            "Mental health": {
                "name_es": "Salud mental",
                "description": "Trastornos psicológicos y emocionales",
                "recommendations": [
                    ("Busca apoyo profesional si es necesario", "medical", 1),
                    ("Mantén una rutina diaria saludable", "lifestyle", 2),
                    ("Practica técnicas de relajación y mindfulness", "lifestyle", 3),
                    ("Mantén conexiones sociales positivas", "social", 4)
                ]
            },
            
            # Endocrinas
            "Hormonal": {
                "name_es": "Hormonal",
                "description": "Trastornos del sistema endocrino",
                "recommendations": [
                    ("Mantén un estilo de vida equilibrado", "lifestyle", 1),
                    ("Realiza chequeos hormonales regulares", "monitoring", 2),
                    ("Sigue una dieta nutritiva y balanceada", "diet", 3),
                    ("Controla el estrés que puede afectar las hormonas", "lifestyle", 4)
                ]
            },
            
            # Oftalmológicas
            "Eye": {
                "name_es": "Ojos",
                "description": "Trastornos oculares",
                "recommendations": [
                    ("Realiza exámenes oculares regulares", "monitoring", 1),
                    ("Protege tus ojos de la luz intensa", "prevention", 2),
                    ("Descansa la vista durante trabajo en pantalla", "lifestyle", 3),
                    ("Mantén una buena higiene ocular", "hygiene", 4)
                ]
            },
            
            # Reproductivas
            "Reproductive": {
                "name_es": "Reproductivo",
                "description": "Trastornos del sistema reproductivo",
                "recommendations": [
                    ("Mantén una buena higiene íntima", "hygiene", 1),
                    ("Realiza chequeos ginecológicos/urológicos regulares", "monitoring", 2),
                    ("Practica relaciones sexuales seguras", "prevention", 3),
                    ("Mantén un estilo de vida saludable", "lifestyle", 4)
                ]
            }
        }
        
        # PASO 3: Insertar todas las enfermedades
        print("📋 Insertando enfermedades...")
        disease_count = 0
        
        for disease_en, data in all_diseases_data.items():
            try:
                cursor.execute("""
                    INSERT INTO diagnoses (name_en, name_es, description_es)
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    name_es = VALUES(name_es),
                    description_es = VALUES(description_es)
                """, (disease_en, data["name_es"], data["description"]))
                disease_count += 1
                print(f"  ✅ {disease_en} → {data['name_es']}")
            except Error as e:
                print(f"  ❌ Error con {disease_en}: {e}")
        
        # PASO 4: Insertar todas las recomendaciones
        print(f"\n💡 Insertando recomendaciones para {disease_count} enfermedades...")
        recommendation_count = 0
        
        for disease_en, data in all_diseases_data.items():
            # Obtener ID de la enfermedad
            cursor.execute("SELECT id FROM diagnoses WHERE name_en = %s", (disease_en,))
            disease_result = cursor.fetchone()
            
            if disease_result:
                disease_id = disease_result[0]
                
                for rec_text, category, priority in data["recommendations"]:
                    try:
                        cursor.execute("""
                            INSERT INTO recommendations 
                            (diagnosis_id, recommendation_text, category, priority, is_active)
                            VALUES (%s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                            recommendation_text = VALUES(recommendation_text),
                            category = VALUES(category),
                            priority = VALUES(priority)
                        """, (disease_id, rec_text, category, priority, True))
                        recommendation_count += 1
                    except Error as e:
                        print(f"  ❌ Error con recomendación de {disease_en}: {e}")
                
                print(f"  ✅ {disease_en}: {len(data['recommendations'])} recomendaciones")
            else:
                print(f"  ❌ No se encontró ID para {disease_en}")
        
        # PASO 5: Confirmar cambios
        db_manager.connection.commit()
        cursor.close()
        
        print(f"\n🎉 === INSERCIÓN COMPLETADA ===")
        print(f"✅ Enfermedades insertadas: {disease_count}")
        print(f"✅ Recomendaciones insertadas: {recommendation_count}")
        
        return True
        
    except Error as e:
        print(f"❌ Error durante la inserción: {e}")
        return False
    finally:
        db_manager.disconnect()

def verify_insertions():
    """Verificar que las inserciones fueron exitosas"""
    
    print("\n🔍 === VERIFICANDO INSERCIONES ===")
    
    if not db_manager.connect():
        print("❌ No se pudo conectar para verificar")
        return
    
    try:
        cursor = db_manager.connection.cursor()
        
        # Contar enfermedades
        cursor.execute("SELECT COUNT(*) FROM diagnoses")
        disease_count = cursor.fetchone()[0]
        
        # Contar recomendaciones
        cursor.execute("SELECT COUNT(*) FROM recommendations WHERE is_active = TRUE")
        rec_count = cursor.fetchone()[0]
        
        print(f"📊 Enfermedades en BD: {disease_count}")
        print(f"📊 Recomendaciones activas: {rec_count}")
        
        # Probar la enfermedad problemática
        print(f"\n🧪 Probando 'Central Nervous System/ Neuromuscular'...")
        recommendations = db_manager.get_recommendations("Central Nervous System/ Neuromuscular")
        print(f"✅ Recomendaciones encontradas: {len(recommendations)}")
        for i, rec in enumerate(recommendations, 1):
            print(f"  {i}. {rec}")
        
        cursor.close()
        
    except Error as e:
        print(f"❌ Error verificando: {e}")
    finally:
        db_manager.disconnect()

if __name__ == "__main__":
    # Ejecutar inserción completa
    if insert_all_diseases_and_recommendations():
        verify_insertions()
    else:
        print("❌ Falló la inserción de datos")