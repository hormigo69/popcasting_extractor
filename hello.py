#!/usr/bin/env python3
"""
Extractor de datos del podcast Popcasting
Extrae información de episodios, playlists y enlaces desde el RSS
"""

import os
import sys

# Añadir el directorio services al path
services_path = os.path.join(os.path.dirname(__file__), "services")
sys.path.insert(0, services_path)

# Importar después de añadir al path
from popcasting_extractor import PopcastingExtractor  # noqa: E402


def main():
    """Función principal del extractor"""
    print("🎵 Extractor de datos de Popcasting 🎵")
    print("=" * 50)

    # Crear instancia del extractor
    extractor = PopcastingExtractor()

    # Ejecutar extracción
    extractor.run()


if __name__ == "__main__":
    main()


# source .venv/bin/activate
