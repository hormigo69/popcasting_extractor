#!/usr/bin/env python3
"""
Script de prueba para el componente AudioManager.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path para importaciones
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.components.audio_manager import AudioManager
from services.supabase_database import SupabaseDatabase
from synology.synology_client import SynologyClient
import logging

def setup_logger():
    """Configura un logger simple para las pruebas."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def test_audio_manager_initialization():
    """Prueba la inicialización del AudioManager."""
    print("🧪 PRUEBA: Inicialización de AudioManager")
    print("-" * 40)
    
    try:
        # Inicializar componentes
        db_manager = SupabaseDatabase()
        synology_client = SynologyClient()
        
        # Crear AudioManager
        audio_manager = AudioManager(db_manager, synology_client)
        
        # Verificar que se creó correctamente
        assert audio_manager.db_manager is not None
        assert audio_manager.synology_client is not None
        assert audio_manager.temp_downloads.exists()
        
        print("✅ AudioManager inicializado correctamente")
        print(f"   - Carpeta temporal: {audio_manager.temp_downloads}")
        
        # Limpiar
        audio_manager.cleanup_temp_folder()
        
        return True
        
    except Exception as e:
        print(f"❌ Error en inicialización: {e}")
        return False


def test_database_connection():
    """Prueba la conexión a la base de datos."""
    print("\n🧪 PRUEBA: Conexión a base de datos")
    print("-" * 40)
    
    try:
        db_manager = SupabaseDatabase()
        
        # Probar obtener podcasts
        podcasts = db_manager.get_all_podcasts()
        
        print(f"✅ Conexión a BD exitosa")
        print(f"   - Podcasts en BD: {len(podcasts)}")
        
        if podcasts:
            # Mostrar información del primer podcast
            first_podcast = podcasts[0]
            print(f"   - Primer podcast: {first_podcast.get('title', 'Sin título')} (ID: {first_podcast['id']})")
            print(f"   - Tiene download_url: {'Sí' if first_podcast.get('download_url') else 'No'}")
            print(f"   - Tiene nas_path: {'Sí' if first_podcast.get('nas_path') else 'No'}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en conexión a BD: {e}")
        return False


def test_synology_connection():
    """Prueba la conexión al NAS Synology."""
    print("\n🧪 PRUEBA: Conexión a Synology NAS")
    print("-" * 40)
    
    try:
        synology_client = SynologyClient()
        
        # Probar login
        if synology_client.login():
            print("✅ Conexión a Synology exitosa")
            
            # Probar listar archivos
            files = synology_client.list_files("/popcasting_marilyn")
            if files is not None:
                print(f"   - Archivos en /popcasting_marilyn: {len(files)}")
            else:
                print("   - No se pudieron listar archivos")
            
            # Logout
            synology_client.logout()
            print("   - Sesión cerrada correctamente")
            
            return True
        else:
            print("❌ Error en login a Synology")
            return False
            
    except Exception as e:
        print(f"❌ Error en conexión a Synology: {e}")
        return False


def test_get_podcasts_with_download_url():
    """Prueba obtener podcasts con URL de descarga."""
    print("\n🧪 PRUEBA: Podcasts con URL de descarga")
    print("-" * 40)
    
    try:
        db_manager = SupabaseDatabase()
        
        # Obtener todos los podcasts
        all_podcasts = db_manager.get_all_podcasts()
        
        # Filtrar podcasts con download_url y program_number
        podcasts_with_download = [
            p for p in all_podcasts 
            if p.get('download_url') and p.get('program_number')
        ]
        
        print(f"✅ Análisis completado")
        print(f"   - Total podcasts: {len(all_podcasts)}")
        print(f"   - Con download_url: {len([p for p in all_podcasts if p.get('download_url')])}")
        print(f"   - Con program_number: {len([p for p in all_podcasts if p.get('program_number')])}")
        print(f"   - Candidatos para archivar: {len(podcasts_with_download)}")
        
        if podcasts_with_download:
            print("\n   📋 Primeros 3 candidatos:")
            for i, podcast in enumerate(podcasts_with_download[:3]):
                program_number = podcast.get('program_number', 'Sin número')
                print(f"     {i+1}. ID: {podcast['id']} - {podcast.get('title', 'Sin título')} (Número: {program_number})")
        
        return True
        
    except Exception as e:
        print(f"❌ Error en análisis: {e}")
        return False


def test_nas_path_generation():
    """Prueba la generación de rutas del NAS."""
    print("\n🧪 PRUEBA: Generación de rutas del NAS")
    print("-" * 40)
    
    try:
        db_manager = SupabaseDatabase()
        synology_client = SynologyClient()
        
        audio_manager = AudioManager(db_manager, synology_client)
        
        # Probar generación de rutas para diferentes números de programa
        test_cases = [1, 42, 100, 999, 1000]
        
        print("📋 Probando generación de rutas:")
        for program_number in test_cases:
            nas_path = audio_manager.get_nas_path_for_podcast(program_number)
            expected_filename = f"popcasting_{program_number:04d}.mp3"
            expected_path = f"/popcasting_marilyn/mp3s/{expected_filename}"
            
            if nas_path == expected_path:
                print(f"   ✅ {program_number:4d} -> {nas_path}")
            else:
                print(f"   ❌ {program_number:4d} -> {nas_path} (esperado: {expected_path})")
                return False
        
        print("✅ Todas las rutas generadas correctamente")
        return True
        
    except Exception as e:
        print(f"❌ Error en prueba de generación de rutas: {e}")
        return False


def run_all_tests():
    """Ejecuta todas las pruebas."""
    print("🧪 INICIANDO PRUEBAS DE AUDIO MANAGER")
    print("=" * 50)
    
    tests = [
        ("Inicialización", test_audio_manager_initialization),
        ("Conexión BD", test_database_connection),
        ("Conexión Synology", test_synology_connection),
        ("Podcasts con download", test_get_podcasts_with_download_url),
        ("Generación rutas NAS", test_nas_path_generation),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ Error inesperado en {test_name}: {e}")
            results.append((test_name, False))
    
    # Resumen de resultados
    print("\n📊 RESUMEN DE PRUEBAS")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASÓ" if result else "❌ FALLÓ"
        print(f"{test_name:20} {status}")
        if result:
            passed += 1
    
    print(f"\nTotal: {passed}/{len(results)} pruebas pasaron")
    
    if passed == len(results):
        print("🎉 ¡Todas las pruebas pasaron!")
        return True
    else:
        print("⚠️ Algunas pruebas fallaron")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1) 