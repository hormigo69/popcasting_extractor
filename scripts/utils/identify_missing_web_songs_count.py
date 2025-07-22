#!/usr/bin/env python3
"""
import sys
from pathlib import Path
from dotenv import load_dotenv
from config import DATABASE_TYPE
from database import get_db_connection, initialize_database
from supabase_database import get_supabase_connection

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services"))

Script para identificar episodios que no tienen web_songs_count.
"""

# Cargar variables de entorno
load_dotenv()

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent.parent))

# Importar directamente los módulos


def get_database_wrapper():
    """
    Obtiene la instancia de base de datos correcta según la configuración.
    """
    if DATABASE_TYPE == "supabase":
        return get_supabase_connection()
    else:
        initialize_database()

        # Crear un wrapper para mantener compatibilidad con la interfaz
        class DatabaseWrapper:
            def __init__(self, conn):
                self.conn = conn
                self.cursor = conn.cursor()

            def get_all_podcasts(self):
                self.cursor.execute("SELECT * FROM podcasts ORDER BY program_number")
                return [dict(row) for row in self.cursor.fetchall()]

            def get_podcast_web_info(self, podcast_id):
                self.cursor.execute(
                    "SELECT wordpress_url, cover_image_url, web_extra_links, web_playlist, web_songs_count, last_web_check FROM podcasts WHERE id = ?",
                    (podcast_id,),
                )
                result = self.cursor.fetchone()
                return dict(result) if result else None

        return DatabaseWrapper(get_db_connection())


def identify_missing_web_songs_count():
    """
    Identifica episodios que no tienen web_songs_count.
    """
    try:
        db = get_database_wrapper()
        print("✅ Conexión a la base de datos establecida")

        # Obtener todos los episodios
        podcasts = db.get_all_podcasts()

        missing_web_songs_count = []
        missing_web_playlist = []

        print(f"\n📊 Analizando {len(podcasts)} episodios...")

        for podcast in podcasts:
            web_info = db.get_podcast_web_info(podcast["id"])

            if not web_info:
                missing_web_playlist.append(podcast)
                continue

            if web_info.get("web_songs_count") is None:
                missing_web_songs_count.append(podcast)

        # Mostrar resultados
        print("\n📈 RESULTADOS")
        print("=" * 50)
        print(f"Total de episodios: {len(podcasts)}")
        print(f"Episodios sin web_songs_count: {len(missing_web_songs_count)}")
        print(f"Episodios sin web_playlist: {len(missing_web_playlist)}")

        if missing_web_songs_count:
            print("\n🎵 Episodios sin web_songs_count:")
            print("-" * 40)
            for podcast in missing_web_songs_count:
                print(
                    f"  #{podcast['program_number']:>3} | {podcast['date']} | {podcast['title'][:50]}..."
                )

        if missing_web_playlist:
            print("\n🌐 Episodios sin web_playlist:")
            print("-" * 40)
            for podcast in missing_web_playlist:
                print(
                    f"  #{podcast['program_number']:>3} | {podcast['date']} | {podcast['title'][:50]}..."
                )

        # Identificar episodios antiguos (0-91) que podrían estar en los HTML
        ancient_episodes = []
        for podcast in missing_web_songs_count + missing_web_playlist:
            try:
                program_number = int(podcast["program_number"])
                if program_number <= 91:
                    ancient_episodes.append(podcast)
            except (ValueError, TypeError):
                continue

        if ancient_episodes:
            print("\n📚 Episodios antiguos (0-91) que podrían estar en HTML:")
            print("-" * 50)
            for podcast in sorted(
                ancient_episodes, key=lambda x: int(x["program_number"])
            ):
                print(
                    f"  #{podcast['program_number']:>3} | {podcast['date']} | {podcast['title'][:50]}..."
                )

        return missing_web_songs_count, missing_web_playlist, ancient_episodes

    except Exception as e:
        print(f"❌ Error: {e}")
        return [], [], []


def main():
    """Función principal del script."""
    print("🔍 Identificador de episodios sin web_songs_count")
    print("=" * 50)

    missing_songs_count, missing_playlist, ancient_episodes = (
        identify_missing_web_songs_count()
    )

    if ancient_episodes:
        print("\n💡 SUGERENCIA:")
        print(
            "Los episodios antiguos (0-91) podrían tener sus playlists en los archivos HTML:"
        )
        print("  - data/00-20.html")
        print("  - data/21-41.html")
        print("  - data/42-63.html")
        print("  - data/64-91.html")

    print("\n✅ Análisis completado")


if __name__ == "__main__":
    main()
