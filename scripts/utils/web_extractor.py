#!/usr/bin/env python3
"""
import sys
from pathlib import Path
    from services.web_cli import main

sys.path.insert(0, str(project_root))

Script principal para extraer información de la web de Popcasting.
"""

# Añadir el directorio del proyecto al path
project_root = Path(__file__).parent.parent.parent

try:
    pass
except ImportError:
    print("Error: No se pudo importar services.web_cli")
    sys.exit(1)

if __name__ == "__main__":
    main()
