#!/usr/bin/env python3
"""
import sys
from pathlib import Path

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

    from services.web_report_generator import main

sys.path.insert(0, str(project_root))

Script principal para generar reportes de discrepancias web de Popcasting.
"""

# Añadir el directorio del proyecto al path
project_root = Path(__file__).parent.parent.parent

try:
    pass
except ImportError:
    print("Error: No se pudo importar services.web_report_generator")
    sys.exit(1)

if __name__ == "__main__":
    main()
