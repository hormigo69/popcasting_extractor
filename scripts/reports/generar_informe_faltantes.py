#!/usr/bin/env python3
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

Script para generar un informe detallado de episodios faltantes.
Analiza el estado actual de la base de datos y reporta lo que falta.
"""

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

    # Episodios sin información web
    missing = [p for p in podcasts if not p.get("wordpress_url")]

    if missing:
        print("🔍 EPISODIOS SIN INFORMACIÓN WEB")
        print("-" * 40)

        # Ordenar por número de programa
        missing_sorted = sorted(missing, key=lambda x: int(x.get("program_number", 0)))

        for i, podcast in enumerate(missing_sorted, 1):
            program_num = podcast.get("program_number", "N/A")
            title = podcast.get("title", "Sin título")
            date = podcast.get("date", "Sin fecha")
            url = podcast.get("url", "Sin URL")

            print(f"{i:2d}. Episodio #{program_num}")
            print(f"    Título: {title}")
            print(f"    Fecha: {date}")
            print(f"    URL RSS: {url}")
            print()

        print(f"📝 Total episodios faltantes: {len(missing)}")
        print()

        # Análisis por rangos
        print("📈 ANÁLISIS POR RANGOS")
        print("-" * 40)

        ranges = [
            (0, 91, "Episodios antiguos (0-91)"),
            (92, 200, "Episodios medios (92-200)"),
            (201, 400, "Episodios recientes (201-400)"),
            (401, 1000, "Episodios muy recientes (401+)"),
        ]

        for start, end, description in ranges:
            range_missing = [
                p
                for p in missing_sorted
                if start <= int(p.get("program_number", 0)) <= end
            ]
            if range_missing:
                print(f"{description}: {len(range_missing)} episodios faltantes")
                for p in range_missing:
                    print(f"  - #{p.get('program_number')}")

        print()

        # Recomendaciones
        print("💡 RECOMENDACIONES")
        print("-" * 40)

        if len(missing) <= 5:
            print("✅ Excelente! Solo faltan pocos episodios.")
            print("   Recomendación: Búsqueda manual individual.")
        elif len(missing) <= 20:
            print("🟡 Estado bueno. Faltan algunos episodios.")
            print("   Recomendación: Revisar URLs del RSS feed.")
        else:
            print("🔴 Faltan muchos episodios.")
            print("   Recomendación: Revisar proceso de extracción.")

        print()
        print("🔧 ACCIONES SUGERIDAS:")
        print("1. Verificar URLs del RSS feed para episodios faltantes")
        print("2. Buscar manualmente en la web los episodios más antiguos")
        print("3. Revisar si hay episodios especiales o con numeración diferente")
        print("4. Actualizar el proceso de extracción web si es necesario")

    else:
        print("🎉 ¡EXCELENTE! Todos los episodios tienen información web.")
        print("   La base de datos está completa al 100%.")

    print()
    print("=" * 60)
    print("📄 Informe generado automáticamente")
    print("   Sistema: Popcasting Extractor")
    print("   Base de datos: Supabase")


if __name__ == "__main__":
    generar_informe_faltantes()
