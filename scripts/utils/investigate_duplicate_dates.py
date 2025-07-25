#!/usr/bin/env python3
"""
import sys
from services.supabase_database import SupabaseDatabase

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

Script para investigar las fechas duplicadas en Supabase.
"""


# Agregar el directorio raíz al path


def investigate_duplicate_dates():
    """
    Investiga las fechas duplicadas en Supabase.
    """
    print("🔍 INVESTIGANDO FECHAS DUPLICADAS EN SUPABASE")
    print("=" * 60)

    db = SupabaseDatabase()

    try:
        # Obtener todos los podcasts
        podcasts = db.get_all_podcasts()

        print(f"📊 Total de episodios: {len(podcasts)}")

        # Agrupar por fecha
        date_groups = {}
        for podcast in podcasts:
            date = podcast.get("date")
            if date:
                if date not in date_groups:
                    date_groups[date] = []
                date_groups[date].append(podcast)

        # Encontrar fechas con múltiples episodios
        duplicate_dates = {
            date: episodes
            for date, episodes in date_groups.items()
            if len(episodes) > 1
        }

        print(f"\n🔄 Fechas con múltiples episodios: {len(duplicate_dates)}")

        if duplicate_dates:
            print("\n📋 Detalle de fechas duplicadas:")
            for date, episodes in sorted(duplicate_dates.items()):
                print(f"\n📅 {date} ({len(episodes)} episodios):")
                for episode in episodes:
                    print(
                        f"  - ID {episode['id']}: #{episode.get('program_number', 'N/A')} - {episode.get('title', 'Sin título')[:50]}..."
                    )

        # Verificar fechas problemáticas específicas
        problem_dates = [
            "2008-03-15",
            "2008-02-15",
            "2007-12-15",
            "2008-04-01",
            "2008-03-01",
            "2008-12-01",
            "2007-12-01",
        ]

        print("\n🔍 Verificando fechas problemáticas específicas:")
        for date in problem_dates:
            if date in date_groups:
                episodes = date_groups[date]
                print(f"\n📅 {date} ({len(episodes)} episodios):")
                for episode in episodes:
                    print(
                        f"  - ID {episode['id']}: #{episode.get('program_number', 'N/A')} - {episode.get('title', 'Sin título')[:50]}..."
                    )

        # Buscar episodios con fechas en formato DD.MM.YYYY
        print("\n🔍 Episodios con fechas en formato DD.MM.YYYY:")
        dd_mm_yyyy_episodes = []
        for podcast in podcasts:
            date = podcast.get("date")
            if date and "." in str(date):
                dd_mm_yyyy_episodes.append(podcast)

        for episode in dd_mm_yyyy_episodes:
            print(
                f"  - ID {episode['id']}: #{episode.get('program_number', 'N/A')} - {episode.get('date')} - {episode.get('title', 'Sin título')[:50]}..."
            )

        # Recomendaciones
        print("\n💡 RECOMENDACIONES")
        print("-" * 40)

        if duplicate_dates:
            print("❌ Se encontraron fechas duplicadas.")
            print("   Esto indica que hay episodios duplicados o conflictivos.")
            print("\n🔧 Opciones:")
            print("1. Revisar y eliminar episodios duplicados")
            print("2. Asignar fechas únicas a episodios conflictivos")
            print("3. Mantener solo un episodio por fecha")
        else:
            print("✅ No se encontraron fechas duplicadas.")

        if dd_mm_yyyy_episodes:
            print(
                f"\n⚠️  Hay {len(dd_mm_yyyy_episodes)} episodios con fechas en formato DD.MM.YYYY"
            )
            print("   Estos necesitan ser normalizados o eliminados.")

    except Exception as e:
        print(f"❌ Error durante la investigación: {e}")
        raise


def main():
    """Función principal."""
    investigate_duplicate_dates()


if __name__ == "__main__":
    main()
