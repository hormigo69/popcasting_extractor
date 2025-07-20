#!/usr/bin/env python3
"""
Script principal para generar reportes de discrepancias web de Popcasting.
"""

import sys
from pathlib import Path

# Añadir el directorio del proyecto al path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from services.web_report_generator import main
except ImportError:
    print("Error: No se pudo importar services.web_report_generator")
    sys.exit(1)

if __name__ == "__main__":
    main()
