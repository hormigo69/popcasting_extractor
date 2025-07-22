#!/usr/bin/env python3
"""
import re
import sys
from services.supabase_database import SupabaseDatabase

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

Script para analizar la secuencia de fechas y determinar el formato correcto.
"""


# Agregar el directorio raíz al path


def parse_date_ambiguous(date_str):
    """
    Parsea una fecha ambigua (DD.MM.YYYY o MM.DD.YYYY) y devuelve ambas interpretaciones.
    """
    if not date_str or "." not in str(date_str):
        return None, None

    pattern = r"^(\d{1,2})\.(\d{1,2})\.(\d{4})$"
    match = re.match(pattern, str(date_str))

    if not match:
        return None, None

    first, second, year = match.groups()

    # Interpretación 1: DD.MM.YYYY
    try:
        date1 = datetime(int(year), int(second), int(first))
        dd_mm_yyyy = date1.strftime("%Y-%m-%d")
    except ValueError:
        dd_mm_yyyy = None

    # Interpretación 2: MM.DD.YYYY
    try:
        date2 = datetime(int(year), int(first), int(second))
        mm_dd_yyyy = date2.strftime("%Y-%m-%d")
    except ValueError:
        mm_dd_yyyy = None

    return dd_mm_yyyy, mm_dd_yyyy


def analyze_date_sequence():
    """
    Analiza la secuencia de fechas para determinar el formato correcto.
    """
    print("🔍 ANALIZANDO SECUENCIA DE FECHAS")
    print("=" * 60)

    db = SupabaseDatabase()

    try:
        # Obtener todos los podcasts ordenados por número de programa
        podcasts = db.get_all_podcasts()

        # Ordenar por número de programa
        podcasts_sorted = sorted(
            podcasts,
            key=lambda x: int(x.get("program_number", 0))
            if x.get("program_number") and str(x.get("program_number")).isdigit()
            else 0,
        )

        print(f"📊 Total de episodios: {len(podcasts_sorted)}")

        # Encontrar episodios con fechas en formato DD.MM.YYYY
        ambiguous_episodes = []

        for podcast in podcasts_sorted:
            date = podcast.get("date")
            if date and "." in str(date):
                dd_mm_yyyy, mm_dd_yyyy = parse_date_ambiguous(date)
                ambiguous_episodes.append(
                    {
                        "id": podcast["id"],
                        "program_number": podcast.get("program_number"),
                        "original_date": date,
                        "dd_mm_yyyy": dd_mm_yyyy,
                        "mm_dd_yyyy": mm_dd_yyyy,
                        "title": podcast.get("title", "Sin título"),
                    }
                )

        print(f"\n📅 Episodios con fechas ambiguas: {len(ambiguous_episodes)}")

        if ambiguous_episodes:
            print("\n📋 Análisis de fechas ambiguas:")
            for episode in ambiguous_episodes:
                print(
                    f"\n  Episodio #{episode['program_number']} (ID {episode['id']}):"
                )
                print(f"    Original: {episode['original_date']}")
                print(f"    DD.MM.YYYY: {episode['dd_mm_yyyy']}")
                print(f"    MM.DD.YYYY: {episode['mm_dd_yyyy']}")
                print(f"    Título: {episode['title'][:50]}...")

        # Analizar secuencia temporal
        print("\n📈 ANÁLISIS DE SECUENCIA TEMPORAL")
        print("-" * 40)

        # Obtener episodios alrededor de los problemáticos para ver la secuencia
        problem_numbers = [60, 61, 65, 66, 67, 68, 84]

        for problem_num in problem_numbers:
            print(f"\n🔍 Alrededor del episodio #{problem_num}:")

            # Encontrar episodios cercanos
            nearby_episodes = []
            for podcast in podcasts_sorted:
                program_num = (
                    int(podcast.get("program_number", 0))
                    if podcast.get("program_number")
                    and str(podcast.get("program_number")).isdigit()
                    else 0
                )
                if problem_num - 2 <= program_num <= problem_num + 2:
                    nearby_episodes.append(podcast)

            # Mostrar secuencia
            for episode in nearby_episodes:
                program_num = episode.get("program_number")
                date = episode.get("date")
                title = episode.get("title", "Sin título")
                print(f"  #{program_num}: {date} - {title[:40]}...")

        # Verificar si hay conflictos con fechas existentes
        print("\n🔄 VERIFICACIÓN DE CONFLICTOS")
        print("-" * 40)

        all_dates = set()
        for podcast in podcasts:
            date = podcast.get("date")
            if date and "." not in str(date):  # Solo fechas ya normalizadas
                all_dates.add(str(date))

        print(f"Fechas ya normalizadas en BD: {len(all_dates)}")

        for episode in ambiguous_episodes:
            print(f"\n  Episodio #{episode['program_number']}:")
            if episode["dd_mm_yyyy"] in all_dates:
                print(f"    ❌ DD.MM.YYYY ({episode['dd_mm_yyyy']}) ya existe")
            else:
                print(f"    ✅ DD.MM.YYYY ({episode['dd_mm_yyyy']}) disponible")

            if episode["mm_dd_yyyy"] in all_dates:
                print(f"    ❌ MM.DD.YYYY ({episode['mm_dd_yyyy']}) ya existe")
            else:
                print(f"    ✅ MM.DD.YYYY ({episode['mm_dd_yyyy']}) disponible")

        # Recomendación basada en el análisis
        print("\n💡 RECOMENDACIÓN")
        print("-" * 40)

        dd_mm_conflicts = 0
        mm_dd_conflicts = 0

        for episode in ambiguous_episodes:
            if episode["dd_mm_yyyy"] in all_dates:
                dd_mm_conflicts += 1
            if episode["mm_dd_yyyy"] in all_dates:
                mm_dd_conflicts += 1

        if dd_mm_conflicts < mm_dd_conflicts:
            print("✅ Recomendación: Usar formato DD.MM.YYYY")
            print(f"   - Conflictos DD.MM.YYYY: {dd_mm_conflicts}")
            print(f"   - Conflictos MM.DD.YYYY: {mm_dd_conflicts}")
        elif mm_dd_conflicts < dd_mm_conflicts:
            print("✅ Recomendación: Usar formato MM.DD.YYYY")
            print(f"   - Conflictos DD.MM.YYYY: {dd_mm_conflicts}")
            print(f"   - Conflictos MM.DD.YYYY: {mm_dd_conflicts}")
        else:
            print("⚠️  Ambos formatos tienen el mismo número de conflictos")
            print("   Se necesita análisis manual de la secuencia temporal")

    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
        raise


def main():
    """Función principal."""
    analyze_date_sequence()


if __name__ == "__main__":
    main()
