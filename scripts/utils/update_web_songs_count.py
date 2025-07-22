#!/usr/bin/env python3
"""
import json
import sys
from pathlib import Path
from dotenv import load_dotenv
from config import DATABASE_TYPE
from database import get_db_connection, initialize_database
from logger_setup import setup_parser_logger
from supabase_database import get_supabase_connection

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services"))

Script para extraer el número de canciones de web_playlist y actualizar el campo web_songs_count.

Este script:
1. Obtiene todos los episodios que tienen web_playlist pero no web_songs_count
2. Extrae el número de canciones del JSON de web_playlist
3. Actualiza el campo web_songs_count en la base de datos
"""

# Cargar variables de entorno
load_dotenv()

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent.parent))

# Importar directamente los módulos

# Configurar logger
logger = setup_parser_logger()


def extract_songs_count_from_playlist(web_playlist_json: str) -> int:
    """
    Extrae el número de canciones de un JSON de playlist.

    Args:
        web_playlist_json: JSON string con la playlist

    Returns:
        Número de canciones en la playlist
    """
    if not web_playlist_json:
        return 0

    try:
        playlist = json.loads(web_playlist_json)
        if isinstance(playlist, list):
            return len(playlist)
        else:
            logger.warning(f"Formato de playlist inesperado: {type(playlist)}")
            return 0
    except json.JSONDecodeError as e:
        logger.error(f"Error parseando JSON de playlist: {e}")
        return 0
    except Exception as e:
        logger.error(f"Error inesperado procesando playlist: {e}")
        return 0


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
                self.cursor.execute("SELECT * FROM podcasts ORDER BY date DESC")
                return [dict(row) for row in self.cursor.fetchall()]

            def get_podcast_web_info(self, podcast_id):
                self.cursor.execute(
                    "SELECT wordpress_url, cover_image_url, web_extra_links, web_playlist, web_songs_count, last_web_check FROM podcasts WHERE id = ?",
                    (podcast_id,),
                )
                result = self.cursor.fetchone()
                return dict(result) if result else None

            def update_web_info(self, podcast_id, **kwargs):
                update_fields = []
                update_values = []

                for key, value in kwargs.items():
                    if value is not None:
                        update_fields.append(f"{key} = ?")
                        update_values.append(value)

                if update_fields:
                    update_values.append(podcast_id)
                    self.cursor.execute(
                        f"UPDATE podcasts SET {', '.join(update_fields)} WHERE id = ?",
                        update_values,
                    )
                    self.conn.commit()

        return DatabaseWrapper(get_db_connection())


def update_web_songs_count():
    """
    Actualiza el campo web_songs_count para todos los episodios que tienen web_playlist.
    """
    try:
        db = get_database_wrapper()
        print("✅ Conexión a la base de datos establecida")

        # Obtener todos los episodios con web_playlist
        podcasts = db.get_all_podcasts()

        total_episodes = 0
        updated_episodes = 0
        skipped_episodes = 0
        error_episodes = 0

        print(f"\n📊 Procesando {len(podcasts)} episodios...")

        for podcast in podcasts:
            total_episodes += 1

            try:
                # Obtener información web del episodio
                web_info = db.get_podcast_web_info(podcast["id"])

                if not web_info or not web_info.get("web_playlist"):
                    skipped_episodes += 1
                    continue

                # Extraer número de canciones
                songs_count = extract_songs_count_from_playlist(
                    web_info["web_playlist"]
                )

                if songs_count > 0:
                    # Actualizar el campo web_songs_count
                    db.update_web_info(
                        podcast_id=podcast["id"], web_songs_count=songs_count
                    )

                    print(
                        f"✅ Episodio #{podcast['program_number']}: {songs_count} canciones"
                    )
                    updated_episodes += 1
                else:
                    print(
                        f"⚠️  Episodio #{podcast['program_number']}: 0 canciones (saltando)"
                    )
                    skipped_episodes += 1

            except Exception as e:
                error_msg = (
                    f"Error procesando episodio #{podcast['program_number']}: {e}"
                )
                print(f"❌ {error_msg}")
                logger.error(error_msg)
                error_episodes += 1

        # Mostrar resumen
        print("\n📈 RESUMEN")
        print("=" * 50)
        print(f"Total de episodios procesados: {total_episodes}")
        print(f"Episodios actualizados: {updated_episodes}")
        print(f"Episodios saltados (sin playlist): {skipped_episodes}")
        print(f"Errores: {error_episodes}")

        if updated_episodes > 0:
            print(f"\n🎉 ¡Se actualizaron {updated_episodes} episodios exitosamente!")
        else:
            print("\n⚠️  No se actualizó ningún episodio")

    except Exception as e:
        error_msg = f"Error general: {e}"
        print(f"❌ {error_msg}")
        logger.error(error_msg)
        return False

    return True


def verify_web_songs_count():
    """
    Verifica que el campo web_songs_count se haya actualizado correctamente.
    """
    try:
        db = get_database_wrapper()
        print("\n🔍 Verificando actualización de web_songs_count...")

        podcasts = db.get_all_podcasts()

        episodes_with_count = 0
        episodes_without_count = 0
        total_songs = 0

        for podcast in podcasts:
            web_info = db.get_podcast_web_info(podcast["id"])

            if web_info and web_info.get("web_songs_count") is not None:
                episodes_with_count += 1
                total_songs += web_info["web_songs_count"]
            else:
                episodes_without_count += 1

        print("📊 Estadísticas de web_songs_count:")
        print(f"   Episodios con web_songs_count: {episodes_with_count}")
        print(f"   Episodios sin web_songs_count: {episodes_without_count}")
        print(f"   Total de canciones contadas: {total_songs}")

        if episodes_with_count > 0:
            avg_songs = total_songs / episodes_with_count
            print(f"   Promedio de canciones por episodio: {avg_songs:.1f}")

    except Exception as e:
        print(f"❌ Error en verificación: {e}")


def main():
    """Función principal del script."""
    print("🎵 Actualizador de web_songs_count")
    print("=" * 40)

    # Actualizar web_songs_count
    success = update_web_songs_count()

    if success:
        # Verificar la actualización
        verify_web_songs_count()

    print("\n✅ Proceso completado")


if __name__ == "__main__":
    main()
