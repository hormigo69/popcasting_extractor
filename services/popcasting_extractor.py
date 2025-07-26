from datetime import datetime

import feedparser
import requests
from bs4 import BeautifulSoup

# Importamos nuestro nuevo módulo de base de datos
from .config import get_database_module
from .logger_setup import setup_parser_logger, setup_stats_logger
from .utils import extract_extra_links, extract_program_info, parse_playlist_simple
from .audio_duration_extractor import AudioDurationExtractor
from .config_manager import ConfigManager
from synology.synology_client import SynologyClient
from src.components.audio_manager import AudioManager

db = get_database_module()

# Configurar los loggers
parser_logger = setup_parser_logger()
stats_logger = setup_stats_logger()


class PopcastingExtractor:
    def __init__(self):
        self.rss_url = "https://feeds.feedburner.com/Popcasting"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
        )
        
        # Inicializar componentes para el archivado de audio
        try:
            print("Inicializando cliente de Synology...")
            config_manager = ConfigManager()
            synology_credentials = config_manager.get_synology_credentials()
            self.synology_client = SynologyClient(**synology_credentials)
            print("Inicializando gestor de audio...")
            self.audio_manager = AudioManager(db, self.synology_client)
            print("✅ Componentes de audio inicializados correctamente")
        except Exception as e:
            print(f"⚠️  No se pudieron inicializar los componentes de audio: {e}")
            print("El proceso continuará sin archivado de audio")
            self.audio_manager = None

    def extract_and_save_episodes(self):
        """
        Extrae todos los episodios del RSS y los guarda en la base de datos.
        Procesa los episodios uno a uno para ser más eficiente.
        """
        processed_urls = set()

        urls_to_try = [
            self.rss_url,
            "https://www.ivoox.com/podcast-popcasting_fg_f1604_feedRSS_o.xml",
            "https://feeds.feedburner.com/Popcasting?format=xml",
        ]

        total_new_songs = 0

        for url in urls_to_try:
            try:
                print(f"Intentando obtener episodios de: {url}")
                feed = feedparser.parse(url)

                if not feed.entries:
                    print(f"No se encontraron episodios en {url}")
                    continue

                print(
                    f"Encontrados {len(feed.entries)} episodios en {url}. Procesando..."
                )
                for entry in feed.entries:
                    # Usamos la URL del episodio como identificador único para no procesarlo dos veces
                    entry_url = entry.get("link")
                    if not entry_url or entry_url in processed_urls:
                        continue

                    episode_data = self._extract_episode_data(entry)
                    if episode_data:
                        # Añadir podcast a la BBDD. La función se encarga de no duplicar.
                        # Devuelve el ID del podcast, sea nuevo o existente.
                        podcast_id = db.add_podcast_if_not_exists(
                            title=episode_data["title"],
                            date=episode_data[
                                "published_date"
                            ],  # Usamos la fecha normalizada
                            url=episode_data["ivoox_web_url"],
                            program_number=episode_data["program_number"],
                            download_url=episode_data["ivoox_download_url"],
                            file_size=episode_data["file_size"],
                        )

                        # Actualizar canciones solo si han cambiado
                        songs_updated = False
                        if episode_data["playlist"]:
                            songs_updated = db.update_songs_if_changed(
                                podcast_id, episode_data["playlist"]
                            )
                            if songs_updated:
                                total_new_songs += len(episode_data["playlist"])
                                print(
                                    f"✅ Canciones actualizadas para episodio {episode_data['program_number']}"
                                )
                            else:
                                print(
                                    f"⏭️  Canciones sin cambios para episodio {episode_data['program_number']}"
                                )

                        # Actualizar links extras solo si han cambiado
                        links_updated = False
                        if episode_data["extra_links"]:
                            links_updated = db.update_extra_links_if_changed(
                                podcast_id, episode_data["extra_links"]
                            )
                            if links_updated:
                                print(
                                    f"✅ Links extras actualizados para episodio {episode_data['program_number']}"
                                )
                            else:
                                print(
                                    f"⏭️  Links extras sin cambios para episodio {episode_data['program_number']}"
                                )

                        # Extraer duración automáticamente si es un episodio nuevo
                        if episode_data["program_number"]:
                            self._extract_duration_for_episode(episode_data["program_number"])

                        # Iniciar el proceso de archivado de audio si está disponible
                        if self.audio_manager:
                            print(f"Iniciando el proceso de archivado de audio para el podcast ID: {podcast_id}")
                            audio_success = self.audio_manager.archive_podcast_audio(podcast_id=podcast_id)
                            if audio_success:
                                print(f"✅ Audio archivado exitosamente para episodio {episode_data['program_number']}")
                            else:
                                print(f"⚠️  No se pudo archivar el audio para episodio {episode_data['program_number']}")

                        processed_urls.add(entry_url)

            except Exception as e:
                error_msg = f"Error al procesar {url}: {e}"
                print(error_msg)
                stats_logger.error(error_msg)
                continue

        # Registrar estadísticas finales
        stats_logger.info("Proceso de extracción finalizado")
        stats_logger.info(f"Total de episodios procesados: {len(processed_urls)}")
        stats_logger.info(
            f"Total de canciones añadidas/actualizadas: {total_new_songs}"
        )
        stats_logger.info(
            "✅ Sistema de control de cambios activado - solo se actualiza contenido modificado"
        )

        # Limpiar archivos temporales del AudioManager si está disponible
        if self.audio_manager:
            try:
                self.audio_manager.cleanup_temp_folder()
                print("🗑️  Archivos temporales de audio limpiados")
            except Exception as e:
                print(f"⚠️  Error al limpiar archivos temporales: {e}")

        print("Proceso de extracción finalizado.")
        print("📊 Estadísticas guardadas en logs/extraction_stats.log")
        print("⚠️  Errores guardados en logs/parsing_errors.log")

    def _extract_episode_data(self, entry) -> dict | None:
        """Extrae datos de un episodio individual"""
        try:
            # Información básica del episodio
            title = entry.get("title", "")
            description = entry.get("description", "")
            published = entry.get("published", "")

            # Extraer número del programa del título
            program_number = self._extract_program_number(title)

            # Normalizar fecha a un formato estándar YYYY-MM-DD
            published_date = self._normalize_date(published)
            if not published_date:
                print(
                    f"AVISO: No se pudo extraer la fecha para el episodio '{title}'. Saltando."
                )
                return None

            # Extraer enlaces de iVoox
            ivoox_download_url, ivoox_web_url, file_size = self._extract_ivoox_links(
                entry
            )

            # Extraer links extras de la descripción original
            extra_links = extract_extra_links(description)

            # Usar la nueva función para obtener enlaces y texto limpio de una vez
            cleaned_description, _ = self._extract_all_links_and_clean(description)

            # La playlist se extrae del texto ya limpio
            playlist = self._extract_playlist(
                cleaned_description, program_info=self._get_program_identifier(entry)
            )

            return {
                "program_number": program_number,
                "title": title,
                "published_date": published_date,
                "ivoox_download_url": ivoox_download_url,
                "ivoox_web_url": ivoox_web_url,
                "file_size": file_size,
                "playlist": playlist,
                "extra_links": extra_links,
            }
        except Exception as e:
            print(f"Error al procesar episodio: {e}")
            return None

    def _normalize_date(self, published_str: str) -> str | None:
        """
        Parsea la fecha de publicación y la devuelve en formato YYYY-MM-DD.
        Esto nos sirve como clave única para cada programa diario.
        """
        if not published_str:
            return None

        try:
            # feedparser ya debería haber parseado la fecha a un formato estándar
            dt = datetime.strptime(published_str, "%a, %d %b %Y %H:%M:%S %z")
            return dt.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            # Intentar otros formatos si falla
            try:
                # Formato sin zona horaria
                dt = datetime.strptime(published_str, "%a, %d %b %Y %H:%M:%S")
                return dt.strftime("%Y-%m-%d")
            except Exception as e:
                print(f"Error al normalizar fecha '{published_str}': {e}")
                return None

    def _extract_program_number(self, title: str) -> str | None:
        """Extrae el número del programa del título"""
        program_info = extract_program_info(title)
        return program_info.get("number")

    def _extract_ivoox_links(self, entry) -> tuple:
        """Extrae URLs de descarga y web de iVoox, junto con información del archivo"""
        download_url = None
        web_url = None
        file_size = None

        # 1. Buscar en los links del entry (más confiable)
        if hasattr(entry, "links"):
            for link in entry.links:
                href = link.get("href", "")
                if "ivoox" in href.lower():
                    if (
                        link.get("type") == "audio/mpeg"
                        or link.get("rel") == "enclosure"
                    ):
                        download_url = href
                        # Intentar extraer el tamaño del archivo si está disponible
                        if hasattr(link, "length") and link.get("length"):
                            try:
                                file_size = int(link.get("length"))
                            except (ValueError, TypeError):
                                pass
                    else:
                        web_url = href

        # 2. Buscar en enclosures (fallback)
        if not download_url and hasattr(entry, "enclosures"):
            for enclosure in entry.enclosures:
                if "ivoox" in enclosure.get("href", "").lower():
                    download_url = enclosure.get("href")
                    # Intentar extraer el tamaño del archivo
                    if enclosure.get("length"):
                        try:
                            file_size = int(enclosure.get("length"))
                        except (ValueError, TypeError):
                            pass

        # 3. Buscar en el contenido/descripción (último recurso)
        if not web_url or not download_url:
            content = entry.get("description", "") + entry.get("content", [{}])[0].get(
                "value", ""
            )
            soup = BeautifulSoup(content, "html.parser")

            for link in soup.find_all("a", href=True):
                href = link["href"]
                if "ivoox" in href.lower():
                    if not web_url and "audios-mp3" in href:
                        web_url = href
                    if not download_url and (
                        ".mp3" in href or "download" in href.lower()
                    ):
                        download_url = href

        # 4. Si no tenemos web_url, usar el link principal del entry
        if not web_url:
            web_url = entry.get("link")

        return download_url, web_url, file_size

    def _extract_all_links_and_clean(self, description: str) -> (str, list[dict]):
        """
        Limpia el texto de la descripción eliminando HTML.
        El parser simplificado se encarga de la limpieza de enlaces.
        """
        soup = BeautifulSoup(description, "html.parser")
        text = soup.get_text()
        return text, []

    def _extract_playlist(
        self, description: str, program_info: str = "N/A"
    ) -> list[dict]:
        """Extrae la playlist de canciones usando el parser simplificado."""
        return parse_playlist_simple(description, program_info, parser_logger)

    def _get_program_identifier(self, entry) -> str:
        """Devuelve un identificador único para un episodio para usar en logs."""
        title = entry.get("title", "Sin Título")
        date = self._normalize_date(entry.get("published", ""))
        return f"'{title}' ({date or 'Sin Fecha'})"

    def _extract_duration_for_episode(self, program_number: str):
        """
        Extrae automáticamente la duración de un episodio si no la tiene.
        
        Args:
            program_number: Número del episodio
        """
        try:
            # Verificar si el episodio ya tiene duración
            podcast = db.get_podcast_by_program_number(program_number)
            if not podcast:
                print(f"⚠️  No se encontró el episodio #{program_number} en la base de datos")
                return
            
            if podcast.get('duration') is not None and podcast.get('duration') > 0:
                print(f"⏭️  Episodio #{program_number} ya tiene duración: {podcast['duration']} segundos")
                return
            
            print(f"🎵 Extrayendo duración automáticamente para episodio #{program_number}...")
            
            # Usar AudioDurationExtractor para extraer la duración
            with AudioDurationExtractor() as extractor:
                result = extractor.process_single_episode(int(program_number))
                
                if result["success"]:
                    duration_minutes = result["duration"] // 60
                    duration_seconds = result["duration"] % 60
                    print(f"✅ Duración extraída automáticamente: {duration_minutes}:{duration_seconds:02d} ({result['duration']} segundos)")
                else:
                    print(f"❌ No se pudo extraer duración automáticamente: {result['error']}")
                    
        except Exception as e:
            print(f"❌ Error extrayendo duración automática para episodio #{program_number}: {e}")

    def run(self):
        """Ejecuta el proceso completo de extracción y guardado en BBDD."""
        print("Iniciando la base de datos...")
        db.initialize_database()

        print("Iniciando extracción de datos de Popcasting...")
        self.extract_and_save_episodes()
        
        # Cerrar conexión con Synology si está disponible
        if hasattr(self, 'synology_client') and self.synology_client:
            try:
                self.synology_client.logout()
                print("✅ Conexión con Synology cerrada")
            except Exception as e:
                print(f"⚠️  Error al cerrar conexión con Synology: {e}")
        
        print("Proceso completado.")
