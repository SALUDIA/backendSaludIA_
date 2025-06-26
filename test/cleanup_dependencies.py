# cleanup_dependencies.py
import subprocess
import sys

def uninstall_packages(packages):
    """Desinstalar paquetes de forma segura"""
    
    print(f"🧹 LIMPIANDO DEPENDENCIAS INNECESARIAS")
    print("="*50)
    
    # Obtener lista de paquetes instalados
    result = subprocess.run([sys.executable, '-m', 'pip', 'list'], 
                          capture_output=True, text=True)
    installed_packages = result.stdout.lower()
    
    uninstalled = []
    skipped = []
    
    for package in packages:
        package_lower = package.lower()
        
        if package_lower in installed_packages:
            print(f"🗑️ Desinstalando {package}...")
            
            try:
                result = subprocess.run([
                    sys.executable, '-m', 'pip', 'uninstall', package, '-y'
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"   ✅ {package} desinstalado")
                    uninstalled.append(package)
                else:
                    print(f"   ❌ Error desinstalando {package}: {result.stderr}")
                    skipped.append(package)
                    
            except Exception as e:
                print(f"   ❌ Excepción desinstalando {package}: {e}")
                skipped.append(package)
        else:
            print(f"⏭️ {package} no está instalado")
            skipped.append(package)
    
    print(f"\n📊 RESUMEN:")
    print(f"   ✅ Desinstalados: {len(uninstalled)}")
    print(f"   ⏭️ Omitidos: {len(skipped)}")
    
    if uninstalled:
        print(f"\n🎉 Paquetes eliminados:")
        for pkg in uninstalled:
            print(f"   - {pkg}")
    
    return uninstalled, skipped

# Paquetes seguros para desinstalar (NO necesarios para SaludIA)
packages_to_remove = [
    # ML Training (no necesarios en producción)
    'xgboost',
    'lightgbm', 
    'catboost',
    'tensorflow',
    'torch',
    'torchvision',
    'keras',
    
    # Visualización
    'matplotlib',
    'seaborn',
    'plotly',
    'bokeh',
    
    # Jupyter
    'jupyter',
    'notebook',
    'ipykernel',
    'ipython',
    'ipywidgets',
    
    # Procesamiento de imágenes
    'opencv-python',
    'opencv-contrib-python',
    'pillow',
    'imageio',
    'scikit-image',
    
    # Testing y desarrollo
    'pytest',
    'black',
    'flake8',
    'autopep8',
    'mypy',
    
    # Análisis estadístico
    'statsmodels',
    
    # Bases de datos alternativas
    'psycopg2',
    'psycopg2-binary',
    'pymongo',
    
    # Procesamiento distribuido
    'dask',
    'ray',
    
    # Librerías especializadas no usadas
    'networkx',
    'gensim',
    'spacy',
    'transformers'
]

if __name__ == '__main__':
    print("⚠️ ADVERTENCIA: Esto desinstalará paquetes que no son necesarios para SaludIA")
    print("✅ Mantendrá: Flask, scikit-learn, pandas, numpy, mysql-connector, etc.")
    
    response = input("\n¿Continuar? (s/N): ").lower().strip()
    
    if response in ['s', 'si', 'yes', 'y']:
        uninstalled, skipped = uninstall_packages(packages_to_remove)
        
        print(f"\n🎯 PRÓXIMOS PASOS:")
        print(f"1. Ejecutar: pip check")
        print(f"2. Probar: python app.py")
        print(f"3. Si hay errores, reinstalar solo lo necesario")
        
    else:
        print("❌ Operación cancelada")