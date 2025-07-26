#!/usr/bin/env python3
"""
Script de prueba para el sincronizador RSS.
Verifica que todos los componentes funcionen correctamente.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

from main import main
from utils.logger import logger


def test_synchronizer():
    """
    Función de prueba para el sincronizador.
    """
    logger.info("🧪 Iniciando prueba del sincronizador RSS")
    
    try:
        # Ejecutar el sincronizador
        main()
        logger.info("✅ Prueba del sincronizador completada exitosamente")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error en la prueba del sincronizador: {e}")
        return False


if __name__ == "__main__":
    """
    Punto de entrada para la prueba.
    """
    success = test_synchronizer()
    exit(0 if success else 1) 