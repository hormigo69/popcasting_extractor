import os

from dotenv import load_dotenv
from supabase import Client, create_client

# Cargar variables de entorno
load_dotenv()


class SupabaseDatabase:
    """Clase para manejar la base de datos Supabase."""

    def __init__(self):
        """Inicializa la conexión con Supabase."""
        self.project_url = os.getenv("supabase_project_url")
        self.api_key = os.getenv("supabase_api_key")

        if not self.project_url or not self.api_key:
            raise ValueError(
                "Las variables de entorno 'supabase_project_url' y 'supabase_api_key' "
                "deben estar configuradas en el archivo .env"
            )

        self.client: Client = create_client(self.project_url, self.api_key)

    def initialize_database(self):
        """
        Inicializa la base de datos creando las tablas si no existen.
        Nota: En Supabase, las tablas se crean desde el dashboard o usando SQL.
        """
        # Las tablas deben crearse manualmente en Supabase
        # Este método verifica que las tablas existan
        try:
            # Verificar que las tablas existen haciendo una consulta simple
            self.client.table("podcasts").select("id").limit(1).execute()
            self.client.table("songs").select("id").limit(1).execute()
            self.client.table("extra_links").select("id").limit(1).execute()
            print("✅ Base de datos Supabase inicializada correctamente")
        except Exception as e:
            print(f"❌ Error al inicializar la base de datos: {e}")
            print(
                "Asegúrate de que las tablas 'podcasts', 'songs' y 'extra_links' existan en Supabase"
            )
            raise

    def add_podcast_if_not_exists(
        self,
        title: str,
        date: str,
        url: str,
        program_number: str,
        download_url: str = None,
        file_size: int = None,
    ) -> int:
        """
        Añade un nuevo podcast a la base de datos si no existe uno con la misma fecha.
        Devuelve el ID del podcast (ya sea nuevo o existente).
        """
        # Validar y convertir tipos
        import re
        from datetime import datetime

        # Validar program_number
        if program_number:
            # Limpiar caracteres no numéricos
            cleaned_number = re.sub(r"[^\d]", "", str(program_number))
            if cleaned_number:
                program_number = int(cleaned_number)
            else:
                program_number = None

        # Validar date
        if date:
            try:
                # Intentar parsear la fecha
                dt = datetime.strptime(date, "%Y-%m-%d")
                date = dt.strftime("%Y-%m-%d")
            except ValueError:
                # Si no es formato YYYY-MM-DD, intentar otros formatos
                date_formats = ["%d/%m/%Y", "%d.%m.%Y", "%Y/%m/%d", "%d-%m-%Y"]
                for fmt in date_formats:
                    try:
                        dt = datetime.strptime(date, fmt)
                        date = dt.strftime("%Y-%m-%d")
                        break
                    except ValueError:
                        continue
                else:
                    # Si no se puede parsear, usar fecha por defecto
                    date = "2005-01-01"

        try:
            # Verificar si ya existe un podcast con esa fecha
            response = (
                self.client.table("podcasts").select("id").eq("date", date).execute()
            )

            if response.data:
                podcast_id = response.data[0]["id"]
                # Actualizar información de links si no estaba disponible antes
                update_data = {}
                if download_url:
                    update_data["download_url"] = download_url
                if file_size:
                    update_data["file_size"] = file_size

                if update_data:
                    self.client.table("podcasts").update(update_data).eq(
                        "id", podcast_id
                    ).execute()
            else:
                # Si no existe, lo insertamos
                insert_data = {
                    "title": title,
                    "date": date,
                    "url": url,
                    "program_number": program_number,
                    "download_url": download_url,
                    "file_size": file_size,
                }
                response = self.client.table("podcasts").insert(insert_data).execute()
                podcast_id = response.data[0]["id"]

            return podcast_id

        except Exception as e:
            print(f"❌ Error al añadir podcast: {e}")
            raise

    def add_song(self, podcast_id: int, title: str, artist: str, position: int):
        """Añade una canción asociada a un podcast."""
        try:
            song_data = {
                "podcast_id": podcast_id,
                "title": title,
                "artist": artist,
                "position": position,
            }
            self.client.table("songs").insert(song_data).execute()
        except Exception as e:
            print(f"❌ Error al añadir canción: {e}")
            raise

    def delete_songs_by_podcast_id(self, podcast_id: int):
        """Borra todas las canciones asociadas a un ID de podcast."""
        try:
            self.client.table("songs").delete().eq("podcast_id", podcast_id).execute()
        except Exception as e:
            print(f"❌ Error al borrar canciones: {e}")
            raise

    def add_extra_link(self, podcast_id: int, text: str, url: str):
        """Añade un link extra asociado a un podcast."""
        try:
            link_data = {"podcast_id": podcast_id, "text": text, "url": url}
            self.client.table("extra_links").insert(link_data).execute()
        except Exception as e:
            print(f"❌ Error al añadir link extra: {e}")
            raise

    def delete_extra_links_by_podcast_id(self, podcast_id: int):
        """Borra todos los links extras asociados a un ID de podcast."""
        try:
            self.client.table("extra_links").delete().eq(
                "podcast_id", podcast_id
            ).execute()
        except Exception as e:
            print(f"❌ Error al borrar links extras: {e}")
            raise

    def get_extra_links_by_podcast_id(self, podcast_id: int) -> list[dict]:
        """Obtiene todos los links extras de un podcast específico."""
        try:
            response = (
                self.client.table("extra_links")
                .select("text, url")
                .eq("podcast_id", podcast_id)
                .order("id")
                .execute()
            )
            return response.data
        except Exception as e:
            print(f"❌ Error al obtener links extras: {e}")
            raise

    def search_songs(self, query: str) -> list[dict]:
        """
        Busca canciones por título o artista.
        La búsqueda no distingue mayúsculas/minúsculas.
        Devuelve una lista de diccionarios con la canción y la info del podcast.
        """
        try:
            # En Supabase, usamos ilike para búsqueda case-insensitive
            response = (
                self.client.table("songs")
                .select(
                    "title, artist, position, podcasts!inner(title, date, program_number)"
                )
                .or_(f"title.ilike.%{query}%,artist.ilike.%{query}%")
                .execute()
            )

            results = []
            for song in response.data:
                podcast_info = song.get("podcasts", {})
                results.append(
                    {
                        "song_title": song["title"],
                        "artist": song["artist"],
                        "position": song["position"],
                        "podcast_title": podcast_info.get("title"),
                        "podcast_date": podcast_info.get("date"),
                        "program_number": podcast_info.get("program_number"),
                    }
                )

            return results

        except Exception as e:
            print(f"❌ Error al buscar canciones: {e}")
            raise

    def search_by_artist(self, artist_query: str) -> list[dict]:
        """
        Busca canciones por artista específico.
        Devuelve una lista de diccionarios con la canción y la info del podcast.
        """
        try:
            response = (
                self.client.table("songs")
                .select(
                    "title, artist, position, podcasts!inner(title, date, program_number)"
                )
                .ilike("artist", f"%{artist_query}%")
                .execute()
            )

            results = []
            for song in response.data:
                podcast_info = song.get("podcasts", {})
                results.append(
                    {
                        "song_title": song["title"],
                        "artist": song["artist"],
                        "position": song["position"],
                        "podcast_title": podcast_info.get("title"),
                        "podcast_date": podcast_info.get("date"),
                        "program_number": podcast_info.get("program_number"),
                    }
                )

            return results

        except Exception as e:
            print(f"❌ Error al buscar por artista: {e}")
            raise

    def get_all_podcasts(self) -> list[dict]:
        """Obtiene todos los podcasts ordenados por fecha (más recientes primero)."""
        try:
            response = (
                self.client.table("podcasts")
                .select("*")
                .order("date", desc=True)
                .execute()
            )
            return response.data
        except Exception as e:
            print(f"❌ Error al obtener podcasts: {e}")
            raise

    def get_songs_by_podcast_id(self, podcast_id: int) -> list[dict]:
        """Obtiene todas las canciones de un podcast específico."""
        try:
            response = (
                self.client.table("songs")
                .select("*")
                .eq("podcast_id", podcast_id)
                .order("position")
                .execute()
            )
            return response.data
        except Exception as e:
            print(f"❌ Error al obtener canciones del podcast: {e}")
            raise

    def get_podcast_by_id(self, podcast_id: int) -> dict | None:
        """Obtiene un podcast específico por su ID."""
        try:
            response = (
                self.client.table("podcasts").select("*").eq("id", podcast_id).execute()
            )
            return response.data[0] if response.data else None
        except Exception as e:
            print(f"❌ Error al obtener podcast por ID: {e}")
            raise

    def songs_have_changed(self, podcast_id: int, new_songs: list[dict]) -> bool:
        """Verifica si las canciones de un podcast han cambiado."""
        try:
            current_songs = self.get_songs_by_podcast_id(podcast_id)

            if len(current_songs) != len(new_songs):
                return True

            for i, new_song in enumerate(new_songs):
                current_song = current_songs[i]
                if (
                    current_song["title"] != new_song["title"]
                    or current_song["artist"] != new_song["artist"]
                    or current_song["position"] != new_song["position"]
                ):
                    return True

            return False

        except Exception as e:
            print(f"❌ Error al verificar cambios en canciones: {e}")
            raise

    def extra_links_have_changed(self, podcast_id: int, new_links: list[dict]) -> bool:
        """Verifica si los links extras de un podcast han cambiado."""
        try:
            current_links = self.get_extra_links_by_podcast_id(podcast_id)

            if len(current_links) != len(new_links):
                return True

            for i, new_link in enumerate(new_links):
                current_link = current_links[i]
                if (
                    current_link["text"] != new_link["text"]
                    or current_link["url"] != new_link["url"]
                ):
                    return True

            return False

        except Exception as e:
            print(f"❌ Error al verificar cambios en links extras: {e}")
            raise

    def update_songs_if_changed(self, podcast_id: int, new_songs: list[dict]) -> bool:
        """Actualiza las canciones de un podcast si han cambiado."""
        try:
            if self.songs_have_changed(podcast_id, new_songs):
                self.delete_songs_by_podcast_id(podcast_id)
                for song in new_songs:
                    self.add_song(
                        podcast_id, song["title"], song["artist"], song["position"]
                    )
                return True
            return False
        except Exception as e:
            print(f"❌ Error al actualizar canciones: {e}")
            raise

    def update_extra_links_if_changed(
        self, podcast_id: int, new_links: list[dict]
    ) -> bool:
        """Actualiza los links extras de un podcast si han cambiado."""
        try:
            if self.extra_links_have_changed(podcast_id, new_links):
                self.delete_extra_links_by_podcast_id(podcast_id)
                for link in new_links:
                    self.add_extra_link(podcast_id, link["text"], link["url"])
                return True
            return False
        except Exception as e:
            print(f"❌ Error al actualizar links extras: {e}")
            raise

    def update_web_info(
        self,
        podcast_id: int,
        wordpress_url: str = None,
        cover_image_url: str = None,
        web_extra_links: str = None,
        web_playlist: str = None,
        web_songs_count: int = None,
    ):
        """Actualiza la información web de un podcast."""
        try:
            update_data = {}
            if wordpress_url is not None:
                update_data["wordpress_url"] = wordpress_url
            if cover_image_url is not None:
                update_data["cover_image_url"] = cover_image_url
            if web_extra_links is not None:
                update_data["web_extra_links"] = web_extra_links
            if web_playlist is not None:
                update_data["web_playlist"] = web_playlist
            if web_songs_count is not None:
                update_data["web_songs_count"] = web_songs_count

            if update_data:
                update_data["last_web_check"] = "now()"
                self.client.table("podcasts").update(update_data).eq(
                    "id", podcast_id
                ).execute()

        except Exception as e:
            print(f"❌ Error al actualizar información web: {e}")
            raise

    def get_podcasts_without_web_info(self) -> list[dict]:
        """Obtiene podcasts que no tienen información web."""
        try:
            response = (
                self.client.table("podcasts")
                .select("*")
                .or_(
                    "wordpress_url.is.null,cover_image_url.is.null,web_extra_links.is.null,web_playlist.is.null"
                )
                .execute()
            )
            return response.data
        except Exception as e:
            print(f"❌ Error al obtener podcasts sin información web: {e}")
            raise

    def get_podcast_web_info(self, podcast_id: int) -> dict:
        """Obtiene la información web de un podcast específico."""
        try:
            response = (
                self.client.table("podcasts")
                .select(
                    "wordpress_url, cover_image_url, web_extra_links, web_playlist, web_songs_count, last_web_check"
                )
                .eq("id", podcast_id)
                .execute()
            )

            if response.data:
                return response.data[0]
            return {}

        except Exception as e:
            print(f"❌ Error al obtener información web del podcast: {e}")
            raise


# Instancia global para mantener la misma interfaz que el código existente
_supabase_db = None


def get_supabase_connection() -> SupabaseDatabase:
    """Obtiene una instancia de la base de datos Supabase."""
    global _supabase_db
    if _supabase_db is None:
        _supabase_db = SupabaseDatabase()
    return _supabase_db


def initialize_database():
    """Inicializa la base de datos Supabase."""
    db = get_supabase_connection()
    db.initialize_database()


def add_podcast_if_not_exists(*args, **kwargs):
    """Wrapper para mantener compatibilidad con el código existente."""
    db = get_supabase_connection()
    return db.add_podcast_if_not_exists(*args, **kwargs)


def add_song(*args, **kwargs):
    """Wrapper para mantener compatibilidad con el código existente."""
    db = get_supabase_connection()
    return db.add_song(*args, **kwargs)


def delete_songs_by_podcast_id(*args, **kwargs):
    """Wrapper para mantener compatibilidad con el código existente."""
    db = get_supabase_connection()
    return db.delete_songs_by_podcast_id(*args, **kwargs)


def add_extra_link(*args, **kwargs):
    """Wrapper para mantener compatibilidad con el código existente."""
    db = get_supabase_connection()
    return db.add_extra_link(*args, **kwargs)


def delete_extra_links_by_podcast_id(*args, **kwargs):
    """Wrapper para mantener compatibilidad con el código existente."""
    db = get_supabase_connection()
    return db.delete_extra_links_by_podcast_id(*args, **kwargs)


def get_extra_links_by_podcast_id(*args, **kwargs):
    """Wrapper para mantener compatibilidad con el código existente."""
    db = get_supabase_connection()
    return db.get_extra_links_by_podcast_id(*args, **kwargs)


def search_songs(*args, **kwargs):
    """Wrapper para mantener compatibilidad con el código existente."""
    db = get_supabase_connection()
    return db.search_songs(*args, **kwargs)


def search_by_artist(*args, **kwargs):
    """Wrapper para mantener compatibilidad con el código existente."""
    db = get_supabase_connection()
    return db.search_by_artist(*args, **kwargs)


def get_all_podcasts(*args, **kwargs):
    """Wrapper para mantener compatibilidad con el código existente."""
    db = get_supabase_connection()
    return db.get_all_podcasts(*args, **kwargs)


def get_songs_by_podcast_id(*args, **kwargs):
    """Wrapper para mantener compatibilidad con el código existente."""
    db = get_supabase_connection()
    return db.get_songs_by_podcast_id(*args, **kwargs)


def get_podcast_by_id(*args, **kwargs):
    """Wrapper para mantener compatibilidad con el código existente."""
    db = get_supabase_connection()
    return db.get_podcast_by_id(*args, **kwargs)


def songs_have_changed(*args, **kwargs):
    """Wrapper para mantener compatibilidad con el código existente."""
    db = get_supabase_connection()
    return db.songs_have_changed(*args, **kwargs)


def extra_links_have_changed(*args, **kwargs):
    """Wrapper para mantener compatibilidad con el código existente."""
    db = get_supabase_connection()
    return db.extra_links_have_changed(*args, **kwargs)


def update_songs_if_changed(*args, **kwargs):
    """Wrapper para mantener compatibilidad con el código existente."""
    db = get_supabase_connection()
    return db.update_songs_if_changed(*args, **kwargs)


def update_extra_links_if_changed(*args, **kwargs):
    """Wrapper para mantener compatibilidad con el código existente."""
    db = get_supabase_connection()
    return db.update_extra_links_if_changed(*args, **kwargs)


def update_web_info(*args, **kwargs):
    """Wrapper para mantener compatibilidad con el código existente."""
    db = get_supabase_connection()
    return db.update_web_info(*args, **kwargs)


def get_podcasts_without_web_info(*args, **kwargs):
    """Wrapper para mantener compatibilidad con el código existente."""
    db = get_supabase_connection()
    return db.get_podcasts_without_web_info(*args, **kwargs)


def get_podcast_web_info(*args, **kwargs):
    """Wrapper para mantener compatibilidad con el código existente."""
    db = get_supabase_connection()
    return db.get_podcast_web_info(*args, **kwargs)
