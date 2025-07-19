#!/usr/bin/env python3
"""
Script principal para generar reportes de discrepancias web de Popcasting.
"""

import sys
from pathlib import Path

# Añadir el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from services.web_report_generator import main

if __name__ == "__main__":
    main()
