#!/usr/bin/env python3
"""
Script wrapper para generar informes de episodios faltantes.
"""

import os
import sys

# Agregar el directorio raíz al path
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime

from services.supabase_database import SupabaseDatabase


def generar_informe_faltantes():
    """Genera un informe completo de episodios faltantes."""
    print("📋 INFORME DE EPISODIOS FALTANTES")
    print("=" * 60)
    print(f"Fecha del informe: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Inicializar base de datos
    db = SupabaseDatabase()
    podcasts = db.get_all_podcasts()

    # Estadísticas generales
    total = len(podcasts)
    with_web = len([p for p in podcasts if p.get("wordpress_url")])
    without_web = total - with_web
    coverage = (with_web / total * 100) if total > 0 else 0

    print("📊 ESTADO ACTUAL DE LA BASE DE DATOS")
    print("-" * 40)
    print(f"Total episodios: {total}")
    print(f"Con información web: {with_web}")
    print(f"Sin información web: {without_web}")
    print(f"Cobertura: {coverage:.1f}%")
    print()

    if without_web == 0:
        print("🎉 ¡EXCELENTE! Todos los episodios tienen información web.")
        print("   La base de datos está completa al 100%.")
    else:
        print("🔍 EPISODIOS SIN INFORMACIÓN WEB")
        print("-" * 40)

        # Episodios sin información web
        missing = [p for p in podcasts if not p.get("wordpress_url")]
        missing_sorted = sorted(missing, key=lambda x: int(x.get("program_number", 0)))

        for i, podcast in enumerate(missing_sorted, 1):
            program_num = podcast.get("program_number", "N/A")
            title = podcast.get("title", "Sin título")
            date = podcast.get("date", "Sin fecha")
            print(f"{i:2d}. Episodio #{program_num} - {title} ({date})")

        print(f"\n📝 Total episodios faltantes: {len(missing)}")

    print()
    print("=" * 60)
    print("📄 Informe generado automáticamente")
    print("   Sistema: Popcasting Extractor")
    print("   Base de datos: Supabase")


if __name__ == "__main__":
    generar_informe_faltantes()
