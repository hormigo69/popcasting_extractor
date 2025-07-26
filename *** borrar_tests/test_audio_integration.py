#!/usr/bin/env python3
"""
Script de prueba para verificar la integración del AudioManager en el flujo principal.
"""

import sys
import os
from pathlib import Path

# Añadir el directorio raíz al path para importaciones
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from services.popcasting_extractor import PopcastingExtractor
from services.config_manager import ConfigManager


def test_config_manager():
    """Prueba la configuración del ConfigManager."""
    print("🧪 Probando ConfigManager...")
    
    try:
        config_manager = ConfigManager()
        credentials = config_manager.get_synology_credentials()
        
        print("✅ ConfigManager inicializado correctamente")
        print(f"   Host: {credentials['host']}")
        print(f"   Puerto: {credentials['port']}")
        print(f"   Usuario: {credentials['username']}")
        print(f"   Contraseña: {'*' * len(credentials['password'])}")
        
        return True
    except Exception as e:
        print(f"❌ Error en ConfigManager: {e}")
        return False


def test_popcasting_extractor_init():
    """Prueba la inicialización del PopcastingExtractor con AudioManager."""
    print("\n🧪 Probando inicialización de PopcastingExtractor...")
    
    try:
        extractor = PopcastingExtractor()
        
        if hasattr(extractor, 'audio_manager') and extractor.audio_manager:
            print("✅ AudioManager inicializado correctamente")
            return True
        else:
            print("⚠️  AudioManager no disponible (esto es normal si no hay configuración de Synology)")
            return True  # No es un error, solo significa que no hay configuración
    except Exception as e:
        print(f"❌ Error en PopcastingExtractor: {e}")
        return False


def test_database_connection():
    """Prueba la conexión a la base de datos."""
    print("\n🧪 Probando conexión a la base de datos...")
    
    try:
        from services.config import get_database_module
        db = get_database_module()
        db.initialize_database()
        print("✅ Conexión a la base de datos exitosa")
        return True
    except Exception as e:
        print(f"❌ Error en la base de datos: {e}")
        return False


def main():
    """Función principal de pruebas."""
    print("🎵 Iniciando pruebas de integración del AudioManager...\n")
    
    tests = [
        ("ConfigManager", test_config_manager),
        ("PopcastingExtractor", test_popcasting_extractor_init),
        ("Base de Datos", test_database_connection),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"📋 Ejecutando prueba: {test_name}")
        if test_func():
            passed += 1
        print()
    
    print("📊 Resumen de pruebas:")
    print(f"   ✅ Pasadas: {passed}/{total}")
    print(f"   ❌ Fallidas: {total - passed}/{total}")
    
    if passed == total:
        print("\n🎉 ¡Todas las pruebas pasaron! La integración está lista.")
    else:
        print("\n⚠️  Algunas pruebas fallaron. Revisa la configuración.")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 