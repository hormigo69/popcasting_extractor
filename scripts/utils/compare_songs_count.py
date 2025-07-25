#!/usr/bin/env python3
"""
Script para comparar el número de canciones en la tabla songs vs web_songs_count en podcasts.
Muestra solo las discrepancias organizadas por capítulo.
"""

import os
import sys
from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


# Añadir el directorio raíz al path para importar los servicios
sys.path.append(str(Path(__file__).parent.parent.parent))

from services.config import DATABASE_TYPE
from services.database import get_db_connection
from services.supabase_database import SupabaseDatabase


def compare_songs_count():
    """Compara el número de canciones vs web_songs_count"""

    db_type = DATABASE_TYPE
    print(f"🔍 Comparando canciones vs web_songs_count usando {db_type}")

    if db_type == "supabase":
        db = SupabaseDatabase()
        discrepancies = compare_supabase_songs_count(db)
    else:
        discrepancies = compare_sqlite_songs_count()

    # Mostrar resultados
    display_discrepancies(discrepancies)

    return discrepancies


def compare_supabase_songs_count(db):
    """Compara canciones vs web_songs_count en Supabase"""

    discrepancies = []

    try:
        # Obtener todos los podcasts con program_number y web_songs_count
        response = (
            db.client.table("podcasts")
            .select("id,program_number,title,date,web_songs_count")
            .not_.is_("program_number", "null")
            .order("program_number")
            .execute()
        )
        podcasts = response.data

        print(f"📊 Analizando {len(podcasts)} podcasts...")

        # Analizar cada podcast
        for podcast in podcasts:
            podcast_id = podcast["id"]
            program_number = podcast["program_number"]
            web_songs_count = podcast["web_songs_count"]
            title = podcast["title"]
            date = podcast["date"]

            # Obtener canciones del podcast
            songs_response = (
                db.client.table("songs")
                .select("id")
                .eq("podcast_id", podcast_id)
                .execute()
            )
            songs = songs_response.data

            actual_songs_count = len(songs)

            # Solo incluir si hay discrepancia
            if web_songs_count is not None and actual_songs_count != web_songs_count:
                discrepancies.append(
                    {
                        "program_number": program_number,
                        "title": title,
                        "date": str(date) if date else None,
                        "web_songs_count": web_songs_count,
                        "actual_songs_count": actual_songs_count,
                        "difference": actual_songs_count - web_songs_count,
                    }
                )

        print("✅ Análisis completado")

    except Exception as e:
        print(f"❌ Error al comparar en Supabase: {e}")
        raise

    return discrepancies


def compare_sqlite_songs_count():
    """Compara canciones vs web_songs_count en SQLite"""

    discrepancies = []

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Obtener todos los podcasts con program_number y web_songs_count
        cursor.execute("""
        SELECT id, program_number, title, date, web_songs_count
        FROM podcasts
        WHERE program_number IS NOT NULL
        ORDER BY program_number
        """)
        podcasts = cursor.fetchall()

        print(f"📊 Analizando {len(podcasts)} podcasts...")

        # Analizar cada podcast
        for podcast in podcasts:
            podcast_id = podcast["id"]
            program_number = podcast["program_number"]
            web_songs_count = podcast["web_songs_count"]
            title = podcast["title"]
            date = podcast["date"]

            # Obtener canciones del podcast
            cursor.execute("SELECT id FROM songs WHERE podcast_id = ?", (podcast_id,))
            songs = cursor.fetchall()

            actual_songs_count = len(songs)

            # Solo incluir si hay discrepancia
            if web_songs_count is not None and actual_songs_count != web_songs_count:
                discrepancies.append(
                    {
                        "program_number": program_number,
                        "title": title,
                        "date": date,
                        "web_songs_count": web_songs_count,
                        "actual_songs_count": actual_songs_count,
                        "difference": actual_songs_count - web_songs_count,
                    }
                )

        conn.close()
        print("✅ Análisis completado")

    except Exception as e:
        print(f"❌ Error al comparar en SQLite: {e}")
        raise

    return discrepancies


def display_discrepancies(discrepancies):
    """Muestra las discrepancias encontradas"""

    if not discrepancies:
        print("\n✅ No se encontraron discrepancias. Todos los conteos coinciden.")
        return

    print(f"\n⚠️ Se encontraron {len(discrepancies)} discrepancias:")
    print("=" * 100)
    print(
        f"{'Capítulo':<8} {'Web Count':<10} {'Actual':<8} {'Diferencia':<12} {'Título'}"
    )
    print("=" * 100)

    # Ordenar por número de programa
    discrepancies.sort(key=lambda x: x["program_number"])

    for disc in discrepancies:
        diff_str = f"{disc['difference']:+d}"
        "🔴" if disc["difference"] < 0 else "🟢" if disc["difference"] > 0 else "🟡"

        print(
            f"{disc['program_number']:<8} {disc['web_songs_count']:<10} {disc['actual_songs_count']:<8} {diff_str:<12} {disc['title'][:50]}..."
        )

    print("=" * 100)

    # Estadísticas
    negative_diff = [d for d in discrepancies if d["difference"] < 0]
    positive_diff = [d for d in discrepancies if d["difference"] > 0]
    zero_diff = [d for d in discrepancies if d["difference"] == 0]

    print("\n📊 Estadísticas de discrepancias:")
    print(f"   🔴 Faltan canciones: {len(negative_diff)} episodios")
    print(f"   🟢 Canciones extra: {len(positive_diff)} episodios")
    print(f"   🟡 Sin diferencia: {len(zero_diff)} episodios")

    # Mostrar los casos más extremos
    if negative_diff:
        max_negative = max(negative_diff, key=lambda x: abs(x["difference"]))
        print(
            f"\n🔴 Mayor déficit: Capítulo {max_negative['program_number']} - Faltan {abs(max_negative['difference'])} canciones"
        )

    if positive_diff:
        max_positive = max(positive_diff, key=lambda x: x["difference"])
        print(
            f"🟢 Mayor exceso: Capítulo {max_positive['program_number']} - {max_positive['difference']} canciones extra"
        )


def main():
    """Función principal"""
    try:
        compare_songs_count()

    except Exception as e:
        print(f"❌ Error en la comparación: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
