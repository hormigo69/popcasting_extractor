#!/usr/bin/env python3
"""
Script rápido para identificar episodios sin web_songs_count.
"""

import sys
from pathlib import Path

from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services"))

# Importar directamente los módulos
from config import DATABASE_TYPE
from database import get_db_connection, initialize_database
from supabase_database import get_supabase_connection


def quick_identify_missing():
    """
    Identifica rápidamente episodios sin web_songs_count.
    """
    try:
        if DATABASE_TYPE == "supabase":
            db = get_supabase_connection()

            # Consulta directa para episodios sin web_songs_count
            response = (
                db.client.table("podcasts")
                .select("id, program_number, title, date, web_songs_count")
                .is_("web_songs_count", "null")
                .execute()
            )

            missing_episodes = response.data

        else:
            initialize_database()
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, program_number, title, date, web_songs_count
                FROM podcasts
                WHERE web_songs_count IS NULL
                ORDER BY program_number
            """)

            missing_episodes = [dict(row) for row in cursor.fetchall()]
            conn.close()

        print(f"📊 Episodios sin web_songs_count: {len(missing_episodes)}")
        print("=" * 50)

        if missing_episodes:
            print("🎵 Lista de episodios faltantes:")
            print("-" * 40)
            for episode in missing_episodes:
                program_num = episode["program_number"]
                date = episode["date"]
                title = episode["title"][:50]
                print(f"  #{program_num:>3} | {date} | {title}...")

            # Identificar episodios antiguos (0-91)
            ancient_episodes = []
            for episode in missing_episodes:
                try:
                    program_number = int(episode["program_number"])
                    if program_number <= 91:
                        ancient_episodes.append(episode)
                except (ValueError, TypeError):
                    continue

            if ancient_episodes:
                print("\n📚 Episodios antiguos (0-91) que podrían estar en HTML:")
                print("-" * 50)
                for episode in sorted(
                    ancient_episodes, key=lambda x: int(x["program_number"])
                ):
                    program_num = episode["program_number"]
                    date = episode["date"]
                    title = episode["title"][:50]
                    print(f"  #{program_num:>3} | {date} | {title}...")

                print("\n💡 SUGERENCIA:")
                print(
                    "Estos episodios podrían tener sus playlists en los archivos HTML:"
                )
                print("  - data/00-20.html")
                print("  - data/21-41.html")
                print("  - data/42-63.html")
                print("  - data/64-91.html")

        return missing_episodes

    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def main():
    """Función principal del script."""
    print("🔍 Identificador rápido de episodios sin web_songs_count")
    print("=" * 60)

    missing_episodes = quick_identify_missing()

    print(f"\n✅ Análisis completado - {len(missing_episodes)} episodios faltantes")


if __name__ == "__main__":
    main()
