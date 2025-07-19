#!/usr/bin/env python3
"""
Script para procesar múltiples episodios de forma automática.
"""

import sys
from pathlib import Path

# Añadir el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from services import database as db
from services.web_extractor import WebExtractor


def main():
    """
    Procesa múltiples episodios de forma automática.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Procesamiento automático de episodios web"
    )
    parser.add_argument(
        "--max-episodes",
        type=int,
        default=10,
        help="Número máximo de episodios a procesar",
    )
    parser.add_argument(
        "--delay", type=float, default=2.0, help="Delay entre requests en segundos"
    )
    parser.add_argument(
        "--start-from", type=int, help="ID del episodio desde donde empezar"
    )

    args = parser.parse_args()

    # Inicializar base de datos
    db.initialize_database()

    print("🚀 Iniciando procesamiento automático de episodios web...")
    print(
        f"📊 Configuración: máximo {args.max_episodes} episodios, delay {args.delay}s"
    )

    extractor = WebExtractor()
    extractor.delay_between_requests = args.delay

    # Procesar episodios
    extractor.extract_all_web_info(max_episodes=args.max_episodes)

    print("\n✅ Procesamiento automático completado!")
    print("💡 Usa 'python web_report.py' para generar un reporte de discrepancias")


if __name__ == "__main__":
    main()
