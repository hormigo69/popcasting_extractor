#!/usr/bin/env python3
"""
Script para migrar datos desde SQLite a Supabase.
Ejecutar después de configurar las variables de entorno y crear las tablas en Supabase.
"""

import os
import sqlite3
import sys
from pathlib import Path

from dotenv import load_dotenv

# Añadir el directorio services al path
sys.path.append(str(Path(__file__).parent.parent / "services"))

from supabase_database import SupabaseDatabase


def get_sqlite_data():
    """Obtiene todos los datos de la base de datos SQLite."""
    db_path = Path(__file__).parent / "popcasting.db"

    if not db_path.exists():
        print("❌ No se encontró la base de datos SQLite (popcasting.db)")
        return None, None, None

    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Obtener podcasts
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM podcasts ORDER BY id")
    podcasts = [dict(row) for row in cursor.fetchall()]

    # Obtener canciones
    cursor.execute("SELECT * FROM songs ORDER BY id")
    songs = [dict(row) for row in cursor.fetchall()]

    # Obtener links extras
    cursor.execute("SELECT * FROM extra_links ORDER BY id")
    extra_links = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return podcasts, songs, extra_links


def migrate_data():
    """Migra los datos de SQLite a Supabase."""
    print("🚀 Iniciando migración de SQLite a Supabase...")

    # Cargar variables de entorno
    load_dotenv()

    # Verificar variables de entorno
    required_vars = ["supabase_project_url", "supabase_api_key"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"❌ Variables de entorno faltantes: {', '.join(missing_vars)}")
        print(
            "Asegúrate de configurar el archivo .env con las credenciales de Supabase"
        )
        return False

    try:
        # Inicializar Supabase
        print("📡 Conectando a Supabase...")
        supabase_db = SupabaseDatabase()
        supabase_db.initialize_database()

        # Obtener datos de SQLite
        print("📂 Leyendo datos de SQLite...")
        podcasts, songs, extra_links = get_sqlite_data()

        if not podcasts:
            print("❌ No se pudieron obtener datos de SQLite")
            return False

        print(
            f"📊 Encontrados {len(podcasts)} podcasts, {len(songs)} canciones, {len(extra_links)} links extras"
        )

        # Migrar podcasts
        print("🔄 Migrando podcasts...")
        podcast_id_mapping = {}  # Mapeo de IDs de SQLite a Supabase

        for podcast in podcasts:
            try:
                new_id = supabase_db.add_podcast_if_not_exists(
                    title=podcast["title"],
                    date=podcast["date"],
                    url=podcast["url"],
                    program_number=podcast["program_number"],
                    download_url=podcast.get("download_url"),
                    file_size=podcast.get("file_size"),
                )
                podcast_id_mapping[podcast["id"]] = new_id
                print(
                    f"  ✅ Podcast '{podcast['title']}' migrado (ID: {podcast['id']} -> {new_id})"
                )
            except Exception as e:
                print(f"  ❌ Error migrando podcast {podcast['id']}: {e}")

        # Migrar canciones
        print("🔄 Migrando canciones...")
        for song in songs:
            try:
                new_podcast_id = podcast_id_mapping.get(song["podcast_id"])
                if new_podcast_id:
                    supabase_db.add_song(
                        podcast_id=new_podcast_id,
                        title=song["title"],
                        artist=song["artist"],
                        position=song["position"],
                    )
                    print(f"  ✅ Canción '{song['title']}' migrada")
                else:
                    print(
                        f"  ⚠️  No se encontró el podcast_id {song['podcast_id']} para la canción {song['id']}"
                    )
            except Exception as e:
                print(f"  ❌ Error migrando canción {song['id']}: {e}")

        # Migrar links extras
        print("🔄 Migrando links extras...")
        for link in extra_links:
            try:
                new_podcast_id = podcast_id_mapping.get(link["podcast_id"])
                if new_podcast_id:
                    supabase_db.add_extra_link(
                        podcast_id=new_podcast_id, text=link["text"], url=link["url"]
                    )
                    print(f"  ✅ Link extra '{link['text']}' migrado")
                else:
                    print(
                        f"  ⚠️  No se encontró el podcast_id {link['podcast_id']} para el link {link['id']}"
                    )
            except Exception as e:
                print(f"  ❌ Error migrando link extra {link['id']}: {e}")

        # Actualizar información web si existe
        print("🔄 Actualizando información web...")
        for podcast in podcasts:
            try:
                new_podcast_id = podcast_id_mapping.get(podcast["id"])
                if new_podcast_id:
                    supabase_db.update_web_info(
                        podcast_id=new_podcast_id,
                        wordpress_url=podcast.get("wordpress_url"),
                        cover_image_url=podcast.get("cover_image_url"),
                        web_extra_links=podcast.get("web_extra_links"),
                        web_playlist=podcast.get("web_playlist"),
                    )
                    if any(
                        podcast.get(field)
                        for field in [
                            "wordpress_url",
                            "cover_image_url",
                            "web_extra_links",
                            "web_playlist",
                        ]
                    ):
                        print(
                            f"  ✅ Información web actualizada para podcast {new_podcast_id}"
                        )
            except Exception as e:
                print(
                    f"  ❌ Error actualizando información web para podcast {podcast['id']}: {e}"
                )

        print("✅ Migración completada exitosamente!")
        print("📊 Resumen:")
        print(f"  - Podcasts migrados: {len(podcast_id_mapping)}")
        print(f"  - Canciones migradas: {len(songs)}")
        print(f"  - Links extras migrados: {len(extra_links)}")

        return True

    except Exception as e:
        print(f"❌ Error durante la migración: {e}")
        return False


def verify_migration():
    """Verifica que la migración fue exitosa."""
    print("🔍 Verificando migración...")

    try:
        supabase_db = SupabaseDatabase()

        # Verificar podcasts
        podcasts = supabase_db.get_all_podcasts()
        print(f"  📊 Podcasts en Supabase: {len(podcasts)}")

        # Verificar canciones
        if podcasts:
            songs = supabase_db.get_songs_by_podcast_id(podcasts[0]["id"])
            print(f"  🎵 Canciones en el primer podcast: {len(songs)}")

        # Verificar links extras
        if podcasts:
            links = supabase_db.get_extra_links_by_podcast_id(podcasts[0]["id"])
            print(f"  🔗 Links extras en el primer podcast: {len(links)}")

        print("✅ Verificación completada")
        return True

    except Exception as e:
        print(f"❌ Error durante la verificación: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🔄 MIGRADOR DE SQLITE A SUPABASE")
    print("=" * 60)

    # Verificar que existe la base de datos SQLite
    db_path = Path(__file__).parent.parent / "popcasting.db"
    if not db_path.exists():
        print("❌ No se encontró la base de datos SQLite (popcasting.db)")
        print("Asegúrate de que el archivo existe en el directorio raíz del proyecto")
        sys.exit(1)

    # Ejecutar migración
    success = migrate_data()

    if success:
        print("\n" + "=" * 60)
        print("🎉 MIGRACIÓN EXITOSA")
        print("=" * 60)

        # Preguntar si quiere verificar
        response = input("\n¿Deseas verificar la migración? (s/n): ").lower().strip()
        if response in ["s", "si", "sí", "y", "yes"]:
            verify_migration()

        print("\n📝 Próximos pasos:")
        print("1. Configura las variables de entorno en el archivo .env")
        print("2. Ejecuta el script SQL en Supabase para crear las tablas")
        print("3. Ejecuta este script para migrar los datos")
        print("4. Actualiza las importaciones en tu código para usar supabase_database")

    else:
        print("\n" + "=" * 60)
        print("❌ MIGRACIÓN FALLIDA")
        print("=" * 60)
        print("Revisa los errores anteriores y vuelve a intentar")
        sys.exit(1)
