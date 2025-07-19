import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from . import database as db
from .logger_setup import setup_parser_logger, setup_stats_logger

# Configurar los loggers
parser_logger = setup_parser_logger()
stats_logger = setup_stats_logger()


class WebExtractor:
    def __init__(self):
        self.base_url = "https://popcastingpop.com"
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            }
        )
        self.delay_between_requests = 1  # segundos

    def extract_all_web_info(self, max_episodes: int = None):
        """
        Extrae información de la web para todos los episodios que no la tienen.
        """
        podcasts = db.get_podcasts_without_web_info()

        if max_episodes:
            podcasts = podcasts[:max_episodes]

        print(f"🔍 Encontrados {len(podcasts)} episodios sin información de web")

        processed = 0
        errors = 0

        for podcast in podcasts:
            try:
                print(
                    f"📄 Procesando episodio {podcast['program_number']} ({podcast['date']})"
                )

                # Intentar encontrar la URL de WordPress
                wordpress_url = self._find_wordpress_url(podcast)

                if wordpress_url:
                    # Extraer información de la página del episodio
                    web_info = self._extract_episode_page_info(wordpress_url)

                    # Actualizar base de datos
                    db.update_web_info(
                        podcast_id=podcast["id"],
                        wordpress_url=wordpress_url,
                        cover_image_url=web_info.get("cover_image_url"),
                        web_extra_links=web_info.get("extra_links_json"),
                        web_playlist=web_info.get("playlist_json"),
                    )

                    print(
                        f"✅ Episodio {podcast['program_number']} procesado correctamente"
                    )
                    processed += 1
                else:
                    print(
                        f"⚠️  No se encontró URL de WordPress para episodio {podcast['program_number']}"
                    )
                    errors += 1

                # Pausa entre requests para ser respetuoso con el servidor
                time.sleep(self.delay_between_requests)

            except Exception as e:
                error_msg = (
                    f"Error procesando episodio {podcast['program_number']}: {e}"
                )
                print(f"❌ {error_msg}")
                parser_logger.error(error_msg)
                errors += 1

        # Registrar estadísticas
        stats_logger.info("Proceso de extracción web finalizado")
        stats_logger.info(f"Episodios procesados: {processed}")
        stats_logger.info(f"Errores: {errors}")

        print(f"\n📊 Resumen: {processed} episodios procesados, {errors} errores")

    def _find_wordpress_url(self, podcast: dict) -> str | None:
        """
        Busca la URL de WordPress para un episodio específico.
        """
        program_number = podcast["program_number"]
        date = podcast["date"]

        # Intentar diferentes patrones de URL
        possible_urls = [
            f"{self.base_url}/{date.replace('-', '/')}/popcasting-{program_number}/",
            f"{self.base_url}/{date[:4]}/{date[5:7]}/{date[8:10]}/popcasting-{program_number}/",
            f"{self.base_url}/popcasting-{program_number}/",
        ]

        for url in possible_urls:
            try:
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    # Verificar que es realmente la página del episodio
                    soup = BeautifulSoup(response.content, "html.parser")
                    if self._is_episode_page(soup, program_number):
                        return url
            except Exception as e:
                parser_logger.warning(f"Error accediendo a {url}: {e}")
                continue

        return None

    def _is_episode_page(self, soup: BeautifulSoup, program_number: str) -> bool:
        """
        Verifica si la página es realmente un episodio del programa especificado.
        """
        # Buscar el número del programa en el contenido
        page_text = soup.get_text().lower()
        if (
            f"popcasting {program_number}" in page_text
            or f"#{program_number}" in page_text
        ):
            return True

        # Buscar en el título
        title = soup.find("title")
        if title and program_number in title.get_text():
            return True

        return False

    def _extract_episode_page_info(self, wordpress_url: str) -> dict:
        """
        Extrae información de la página de un episodio específico.
        """
        try:
            response = self.session.get(wordpress_url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, "html.parser")

            # Extraer imagen de portada
            cover_image_url = self._extract_cover_image(soup)

            # Extraer enlaces extras
            extra_links = self._extract_web_extra_links(soup)
            extra_links_json = self._serialize_links(extra_links)

            # Extraer playlist
            playlist = self._extract_web_playlist(soup)
            playlist_json = self._serialize_playlist(playlist)

            return {
                "cover_image_url": cover_image_url,
                "extra_links_json": extra_links_json,
                "playlist_json": playlist_json,
            }

        except Exception as e:
            parser_logger.error(f"Error extrayendo información de {wordpress_url}: {e}")
            return {}

    def _extract_cover_image(self, soup: BeautifulSoup) -> str | None:
        """
        Extrae la URL de la imagen de portada del episodio.
        """
        # Buscar imágenes en el contenido principal
        content_area = (
            soup.find("div", class_="entry-content")
            or soup.find("article")
            or soup.find("div", class_="entrybody")
        )

        if content_area:
            # Buscar la primera imagen que parezca ser la portada
            images = content_area.find_all("img")
            for img in images:
                src = img.get("src")
                if src:
                    # Verificar si parece ser una imagen de portada (buscar el número del episodio)
                    if (
                        any(
                            keyword in src.lower()
                            for keyword in ["cover", "portada", "thumbnail"]
                        )
                        or "/wp-content/uploads/" in src
                    ):
                        return urljoin(self.base_url, src)

            # Si no encontramos una imagen específica de portada, tomar la primera
            if images:
                src = images[0].get("src")
                if src:
                    return urljoin(self.base_url, src)

        return None

    def _extract_web_extra_links(self, soup: BeautifulSoup) -> list[dict]:
        """
        Extrae los enlaces extras de la página web.
        """
        extra_links = []

        # Buscar enlaces con el estilo específico de Popcasting
        # Los enlaces extras suelen estar en spans con color #ff99cc
        colored_spans = soup.find_all("span", style=lambda x: x and "#ff99cc" in x)

        for span in colored_spans:
            links = span.find_all("a")
            for link in links:
                text = link.get_text(strip=True)
                url = link.get("href")
                if text and url:
                    extra_links.append({"text": text, "url": url})

        # También buscar enlaces en el contenido general
        content_area = soup.find("div", class_="entry-content") or soup.find("article")
        if content_area:
            # Buscar enlaces que no sean de navegación
            links = content_area.find_all("a")
            for link in links:
                text = link.get_text(strip=True)
                url = link.get("href")

                # Filtrar enlaces que parezcan ser extras (no de navegación)
                if (
                    text
                    and url
                    and not any(
                        nav_word in text.lower()
                        for nav_word in [
                            "comentarios",
                            "compartir",
                            "twitter",
                            "facebook",
                        ]
                    )
                    and not url.startswith("#")
                ):
                    # Evitar duplicados
                    if not any(existing["url"] == url for existing in extra_links):
                        extra_links.append({"text": text, "url": url})

        return extra_links

    def _extract_web_playlist(self, soup: BeautifulSoup) -> list[dict]:
        """
        Extrae la playlist de la página web.
        """
        playlist = []

        # Buscar en el contenido principal
        content_area = (
            soup.find("div", class_="entry-content")
            or soup.find("article")
            or soup.find("div", class_="entrybody")
        )

        if content_area:
            # Buscar listas numeradas o con viñetas que contengan canciones
            lists = content_area.find_all(["ol", "ul"])

            for list_elem in lists:
                items = list_elem.find_all("li")
                for i, item in enumerate(items):
                    text = item.get_text(strip=True)

                    # Intentar extraer artista y título de la canción
                    song_info = self._parse_song_text(text)
                    if song_info:
                        playlist.append(
                            {
                                "position": i + 1,
                                "artist": song_info["artist"],
                                "title": song_info["title"],
                            }
                        )

            # Si no encontramos listas, buscar en párrafos
            if not playlist:
                paragraphs = content_area.find_all("p")
                position = 1

                for p in paragraphs:
                    text = p.get_text(strip=True)

                    # Buscar canciones en el texto del párrafo
                    songs = self._parse_popcasting_playlist_text(text)
                    if songs:
                        for i, song in enumerate(songs):
                            playlist.append(
                                {
                                    "position": position + i,
                                    "artist": song["artist"],
                                    "title": song["title"],
                                }
                            )
                        position += len(songs)
                    else:
                        # Intentar extraer una sola canción del párrafo
                        song_info = self._parse_song_text(text)
                        if song_info:
                            playlist.append(
                                {
                                    "position": position,
                                    "artist": song_info["artist"],
                                    "title": song_info["title"],
                                }
                            )
                            position += 1

        return playlist

    def _parse_popcasting_playlist_text(self, text: str) -> list[dict]:
        """
        Parsea el texto específico de Popcasting que contiene múltiples canciones separadas por ::
        """
        songs = []

        # Buscar el patrón específico de Popcasting: artista · título :: artista · título
        if "::" in text:
            # Dividir por ::
            parts = text.split("::")
            for part in parts:
                part = part.strip()
                if part:
                    song_info = self._parse_song_text(part)
                    if song_info:
                        songs.append(song_info)

        return songs

    def _parse_song_text(self, text: str) -> dict | None:
        """
        Parsea el texto para extraer artista y título de una canción.
        """
        # Patrones comunes para canciones
        patterns = [
            r"^(.+?)\s*[-–—]\s*(.+)$",  # Artista - Título
            r"^(.+?)\s*:\s*(.+)$",  # Artista: Título
            r'^(.+?)\s*"\s*(.+?)\s*"$',  # Artista "Título"
            r"^(.+?)\s*·\s*(.+)$",  # Artista · Título (formato de Popcasting)
        ]

        for pattern in patterns:
            match = re.match(pattern, text.strip())
            if match:
                artist = match.group(1).strip()
                title = match.group(2).strip()

                # Filtrar texto que no parece ser una canción
                if (
                    len(artist) > 1
                    and len(title) > 1
                    and not any(
                        word in artist.lower()
                        for word in [
                            "comentarios",
                            "compartir",
                            "twitter",
                            "facebook",
                            "popcasting",
                        ]
                    )
                ):
                    return {"artist": artist, "title": title}

        return None

    def _serialize_links(self, links: list[dict]) -> str:
        """
        Serializa los enlaces extras a JSON string.
        """
        import json

        return json.dumps(links, ensure_ascii=False)

    def _serialize_playlist(self, playlist: list[dict]) -> str:
        """
        Serializa la playlist a JSON string.
        """
        import json

        return json.dumps(playlist, ensure_ascii=False)

    def compare_rss_vs_web(self, podcast_id: int) -> dict:
        """
        Compara la información del RSS con la de la web para detectar discrepancias.
        """
        # Obtener información del RSS
        rss_songs = db.get_songs_by_podcast_id(podcast_id)
        rss_links = db.get_extra_links_by_podcast_id(podcast_id)

        # Obtener información de la web
        web_info = db.get_podcast_web_info(podcast_id)

        if not web_info:
            return {"error": "No hay información de web disponible"}

        discrepancies = {
            "songs_differences": [],
            "links_differences": [],
            "summary": {},
        }

        # Comparar canciones
        if web_info.get("web_playlist"):
            import json

            try:
                web_songs = json.loads(web_info["web_playlist"])
                discrepancies["songs_differences"] = self._compare_songs(
                    rss_songs, web_songs
                )
            except json.JSONDecodeError:
                discrepancies["songs_differences"] = ["Error parseando playlist de web"]

        # Comparar enlaces extras
        if web_info.get("web_extra_links"):
            import json

            try:
                web_links = json.loads(web_info["web_extra_links"])
                discrepancies["links_differences"] = self._compare_links(
                    rss_links, web_links
                )
            except json.JSONDecodeError:
                discrepancies["links_differences"] = ["Error parseando enlaces de web"]

        # Resumen
        discrepancies["summary"] = {
            "rss_songs_count": len(rss_songs),
            "web_songs_count": len(web_songs) if "web_songs" in locals() else 0,
            "rss_links_count": len(rss_links),
            "web_links_count": len(web_links) if "web_links" in locals() else 0,
            "has_discrepancies": bool(
                discrepancies["songs_differences"] or discrepancies["links_differences"]
            ),
        }

        return discrepancies

    def _compare_songs(self, rss_songs: list, web_songs: list) -> list[str]:
        """
        Compara las canciones del RSS con las de la web.
        """
        differences = []

        # Comparar número de canciones
        if len(rss_songs) != len(web_songs):
            differences.append(
                f"Diferente número de canciones: RSS={len(rss_songs)}, Web={len(web_songs)}"
            )

        # Comparar canciones individuales
        min_length = min(len(rss_songs), len(web_songs))
        for i in range(min_length):
            rss_song = rss_songs[i]
            web_song = web_songs[i]

            if (
                rss_song["artist"].lower() != web_song["artist"].lower()
                or rss_song["title"].lower() != web_song["title"].lower()
            ):
                differences.append(
                    f"Canción {i+1}: RSS='{rss_song['artist']} - {rss_song['title']}' vs "
                    f"Web='{web_song['artist']} - {web_song['title']}'"
                )

        return differences

    def _compare_links(self, rss_links: list, web_links: list) -> list[str]:
        """
        Compara los enlaces extras del RSS con los de la web.
        """
        differences = []

        # Comparar número de enlaces
        if len(rss_links) != len(web_links):
            differences.append(
                f"Diferente número de enlaces: RSS={len(rss_links)}, Web={len(web_links)}"
            )

        # Crear sets para comparación
        rss_set = set()
        web_set = set()

        for link in rss_links:
            rss_set.add((link["text"].lower(), link["url"].lower()))

        for link in web_links:
            web_set.add((link["text"].lower(), link["url"].lower()))

        # Encontrar diferencias
        only_in_rss = rss_set - web_set
        only_in_web = web_set - rss_set

        if only_in_rss:
            differences.append(f"Enlaces solo en RSS: {list(only_in_rss)}")
        if only_in_web:
            differences.append(f"Enlaces solo en Web: {list(only_in_web)}")

        return differences
