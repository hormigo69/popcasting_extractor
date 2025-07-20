#!/usr/bin/env python3
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

Extractor especializado para episodios antiguos (0-91) de Popcasting.
Estos episodios están en páginas de archivo con estructura HTML diferente.
"""

import json
import re
import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from services import database as sqlite_db
from services.supabase_database import SupabaseDatabase


class ExtractorEpisodiosAntiguos:
    """Extractor para episodios antiguos (0-91) de las páginas de archivo."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
        )

        # URLs de las páginas de archivo
        self.archivo_urls = {
            "00-20": "https://popcastingpop.com/archivo-popcasting/",
            "21-41": "https://popcastingpop.com/archivo-popcasting-21-40/",
            "42-63": "https://popcastingpop.com/programas-anteriores-42-63/",
            "64-91": "https://popcastingpop.com/programas-anteriores-64-91/",
        }

    def extraer_episodios_de_pagina(self, url: str) -> list[dict]:
        """Extrae todos los episodios de una página de archivo."""
        print(f"📄 Extrayendo episodios de: {url}")

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            episodios = []
            episodios_vistos = set()  # Para evitar duplicados

            # Buscar todos los enlaces de programa (patrón actualizado)
            enlaces_programa = soup.find_all("a", href=re.compile(r"popcasting\d+"))

            for enlace in enlaces_programa:
                try:
                    episodio = self._extraer_episodio_individual(enlace, soup)
                    if episodio and episodio["numero"] not in episodios_vistos:
                        episodios.append(episodio)
                        episodios_vistos.add(episodio["numero"])
                        print(f"  ✅ Episodio #{episodio['numero']} extraído")
                except Exception as e:
                    print(f"  ❌ Error extrayendo episodio: {e}")
                    continue

            print(f"📊 Total episodios extraídos: {len(episodios)}")
            return episodios

        except Exception as e:
            print(f"❌ Error accediendo a {url}: {e}")
            return []

    def _extraer_episodio_individual(
        self, enlace: BeautifulSoup, soup: BeautifulSoup
    ) -> dict | None:
        """Extrae información de un episodio individual."""
        # Extraer número del episodio desde la URL
        href = enlace.get("href", "")
        match = re.search(r"popcasting(\d+)", href)
        if not match:
            return None

        numero = int(match.group(1))

        # Buscar el contenedor del episodio (párrafo padre)
        contenedor = enlace.find_parent("p")
        if not contenedor:
            contenedor = enlace.find_parent("div")

        if not contenedor:
            return None

        # Extraer información del episodio
        episodio = {
            "numero": numero,
            "wordpress_url": enlace.get("href", ""),
            "cover_image_url": self._extraer_imagen_portada(contenedor),
            "fecha": self._extraer_fecha(contenedor),
            "canciones": self._extraer_canciones(contenedor),
            "enlaces_extra": self._extraer_enlaces_extra(contenedor),
            "audio_url": self._extraer_audio_url(contenedor),
            "web_playlist": self._extraer_playlist(contenedor),
        }

        return episodio

    def _extraer_imagen_portada(self, contenedor: BeautifulSoup) -> str:
        """Extrae la URL de la imagen de portada."""
        img = contenedor.find("img")
        if img:
            # Intentar obtener la imagen original
            orig_file = img.get("data-orig-file")
            if orig_file:
                return orig_file

            # Fallback a src
            src = img.get("src")
            if src:
                return src

        return ""

    def _extraer_fecha(self, contenedor: BeautifulSoup) -> str:
        """Extrae la fecha del episodio."""
        # Buscar el párrafo con la fecha (formato [DD.MM.YYYY])
        fecha_pattern = r"\[(\d{1,2}\.\d{1,2}\.\d{4})\]"

        # Buscar en el contenedor y sus hermanos
        elementos = [contenedor] + list(contenedor.find_next_siblings())

        for elemento in elementos:
            if elemento.name in ["p", "div"]:
                texto = elemento.get_text(strip=True)
                match = re.search(fecha_pattern, texto)
                if match:
                    return match.group(1)

        return ""

    def _extraer_canciones(self, contenedor: BeautifulSoup) -> list[str]:
        """Extrae la lista de canciones del episodio."""
        canciones = []

        # Buscar el texto con las canciones (separadas por ::)
        elementos = [contenedor] + list(contenedor.find_next_siblings())

        for elemento in elementos:
            if elemento.name in ["p", "div"]:
                texto = elemento.get_text(strip=True)

                # Verificar si contiene canciones (patrón: artista · canción)
                if "·" in texto and "::" in texto:
                    # Limpiar el texto y dividir por ::
                    canciones_raw = texto.split("::")
                    for cancion_raw in canciones_raw:
                        cancion = cancion_raw.strip()
                        if cancion and "·" in cancion:
                            canciones.append(cancion)

                    if canciones:
                        break

        return canciones

    def _extraer_enlaces_extra(self, contenedor: BeautifulSoup) -> list[str]:
        """Extrae los enlaces extra del episodio."""
        enlaces = []

        # Buscar enlaces en h6 con color verde
        elementos = [contenedor] + list(contenedor.find_next_siblings())

        for elemento in elementos:
            if elemento.name == "h6":
                links = elemento.find_all("a")
                for link in links:
                    href = link.get("href")
                    if href and href.startswith("http"):
                        enlaces.append(href)

        return enlaces

    def _extraer_audio_url(self, contenedor: BeautifulSoup) -> str:
        """Extrae la URL del archivo de audio."""
        # Buscar el elemento audio
        elementos = [contenedor] + list(contenedor.find_next_siblings())

        for elemento in elementos:
            audio = elemento.find("audio")
            if audio:
                source = audio.find("source")
                if source:
                    return source.get("src", "")

        return ""

    def _extraer_playlist(self, contenedor: BeautifulSoup) -> str:
        """Extrae la playlist como JSON."""
        canciones = self._extraer_canciones(contenedor)

        if not canciones:
            return ""

        playlist = []
        for i, cancion in enumerate(canciones, 1):
            # Intentar separar artista y título
            if "·" in cancion:
                partes = cancion.split("·", 1)
                artista = partes[0].strip()
                titulo = partes[1].strip()
            else:
                artista = ""
                titulo = cancion.strip()

            playlist.append(
                {"position": i, "artist": artista, "title": titulo, "duration": None}
            )

        return json.dumps(playlist, ensure_ascii=False)

    def extraer_todos_los_episodios(self) -> list[dict]:
        """Extrae todos los episodios de todas las páginas de archivo."""
        todos_episodios = []

        for rango, url in self.archivo_urls.items():
            print(f"\n🔄 Procesando rango {rango}...")
            episodios = self.extraer_episodios_de_pagina(url)
            todos_episodios.extend(episodios)

            # Pausa entre páginas
            time.sleep(2)

        print(f"\n🎉 Total episodios extraídos: {len(todos_episodios)}")
        return todos_episodios

    def guardar_en_base_datos(self, episodios: list[dict], usar_supabase: bool = True):
        """Guarda los episodios extraídos en la base de datos."""
        if usar_supabase:
            db = SupabaseDatabase()
        else:
            sqlite_db.initialize_database()
            conn = sqlite_db.get_db_connection()

        guardados = 0
        actualizados = 0
        no_encontrados = 0

        for episodio in episodios:
            try:
                if usar_supabase:
                    # Buscar si el episodio ya existe
                    episodios_existentes = db.get_all_podcasts()
                    episodio_existente = None

                    for ep in episodios_existentes:
                        if ep.get("program_number") == episodio["numero"]:
                            episodio_existente = ep
                            break

                    if episodio_existente:
                        # Actualizar episodio existente
                        db.update_web_info(
                            episodio_existente["id"],
                            episodio["wordpress_url"],
                            episodio["cover_image_url"],
                            json.dumps(episodio["enlaces_extra"]),
                            episodio["web_playlist"],
                        )
                        actualizados += 1
                        print(f"  ✅ Episodio #{episodio['numero']} actualizado")
                    else:
                        # Crear nuevo episodio usando add_podcast_if_not_exists
                        try:
                            podcast_id = db.add_podcast_if_not_exists(
                                title=f"Popcasting #{episodio['numero']:03d}",
                                date=episodio["fecha"]
                                if episodio["fecha"]
                                else "2005-01-01",
                                url=episodio["wordpress_url"],
                                program_number=str(episodio["numero"]),
                                download_url=episodio["audio_url"]
                                if episodio["audio_url"]
                                else None,
                            )

                            # Actualizar información web
                            db.update_web_info(
                                podcast_id,
                                episodio["wordpress_url"],
                                episodio["cover_image_url"],
                                json.dumps(episodio["enlaces_extra"]),
                                episodio["web_playlist"],
                            )

                            guardados += 1
                            print(
                                f"  ✅ Episodio #{episodio['numero']} creado y actualizado"
                            )
                        except Exception as e:
                            print(
                                f"  ❌ Error creando episodio #{episodio['numero']}: {e}"
                            )
                            no_encontrados += 1
                else:
                    # SQLite
                    cursor = conn.cursor()

                    # Verificar si existe
                    cursor.execute(
                        "SELECT id FROM podcasts WHERE program_number = ?",
                        (episodio["numero"],),
                    )
                    existente = cursor.fetchone()

                    if existente:
                        # Actualizar
                        cursor.execute(
                            """
                            UPDATE podcasts
                            SET wordpress_url = ?, cover_image_url = ?,
                                web_extra_links = ?, web_playlist = ?,
                                web_last_checked = ?
                            WHERE program_number = ?
                        """,
                            (
                                episodio["wordpress_url"],
                                episodio["cover_image_url"],
                                json.dumps(episodio["enlaces_extra"]),
                                episodio["web_playlist"],
                                datetime.now().isoformat(),
                                episodio["numero"],
                            ),
                        )
                        actualizados += 1
                        print(f"  ✅ Episodio #{episodio['numero']} actualizado")
                    else:
                        no_encontrados += 1
                        print(
                            f"  ⚠️  Episodio #{episodio['numero']} no encontrado en BD (saltando)"
                        )

            except Exception as e:
                print(f"  ❌ Error guardando episodio #{episodio['numero']}: {e}")
                continue

        if not usar_supabase:
            conn.commit()
            conn.close()

        print("\n📊 Resumen:")
        print(f"  - Episodios actualizados: {actualizados}")
        print(f"  - Episodios creados: {guardados}")
        print(f"  - Episodios no procesados: {no_encontrados}")
        print(f"  - Total procesados: {actualizados + guardados + no_encontrados}")


def main():
    """Función principal."""
    print("🎵 EXTRACTOR DE EPISODIOS ANTIGUOS (0-91)")
    print("=" * 50)

    extractor = ExtractorEpisodiosAntiguos()

    # Extraer todos los episodios
    episodios = extractor.extraer_todos_los_episodios()

    if episodios:
        print(f"\n💾 Guardando {len(episodios)} episodios en la base de datos...")
        extractor.guardar_en_base_datos(episodios, usar_supabase=True)
        print("✅ Proceso completado exitosamente!")
    else:
        print("❌ No se encontraron episodios para extraer")


if __name__ == "__main__":
    main()
