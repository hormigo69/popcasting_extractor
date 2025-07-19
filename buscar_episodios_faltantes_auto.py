#!/usr/bin/env python3
"""
Script para buscar automáticamente los episodios faltantes en las páginas de archivo.
"""

import json
import re

import requests
from bs4 import BeautifulSoup

from services.supabase_database import SupabaseDatabase


class BuscadorEpisodiosFaltantes:
    """Buscador automático de episodios faltantes."""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
        )
        self.db = SupabaseDatabase()

        # Episodios faltantes que necesitamos encontrar
        self.episodios_faltantes = [
            "61",
            "062",
            "62",
            "63",
            "65",
            "66",
            "67",
            "68",
            "70",
            "84",
        ]

        # URLs de las páginas de archivo
        self.paginas_archivo = [
            "https://popcastingpop.com/archivo-popcasting/",
            "https://popcastingpop.com/archivo-popcasting-21-40/",
            "https://popcastingpop.com/programas-anteriores-42-63/",
            "https://popcastingpop.com/programas-anteriores-64-91/",
        ]

    def buscar_episodios_en_pagina(self, url: str):
        """Busca episodios faltantes en una página específica."""
        print(f"🔍 Buscando en: {url}")

        try:
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")

            episodios_encontrados = []

            # Buscar todos los enlaces de programa
            enlaces = soup.find_all("a", href=re.compile(r"popcasting\d+"))

            for enlace in enlaces:
                href = enlace.get("href", "")
                match = re.search(r"popcasting(\d+)", href)

                if match:
                    numero = match.group(1)
                    if numero in self.episodios_faltantes:
                        print(f"  ✅ Encontrado episodio #{numero}")

                        # Extraer información del episodio
                        info = self._extraer_info_episodio(enlace, soup)
                        if info:
                            episodios_encontrados.append(
                                {"numero": numero, "url_ivoox": href, "info": info}
                            )

            return episodios_encontrados

        except Exception as e:
            print(f"  ❌ Error accediendo a {url}: {e}")
            return []

    def _extraer_info_episodio(self, enlace, soup):
        """Extrae información de un episodio individual."""
        try:
            # Buscar el contenedor del episodio (puede estar cerca del enlace)
            contenedor = (
                enlace.find_parent("div") or enlace.find_parent("p") or enlace.parent
            )

            if not contenedor:
                return None

            # Buscar imagen de portada
            img = contenedor.find("img")
            cover_image_url = None
            if img and img.get("data-orig-file"):
                cover_image_url = img.get("data-orig-file")
            elif img and img.get("src"):
                cover_image_url = img.get("src")

            # Buscar fecha
            fecha = None
            fecha_elem = contenedor.find("p", string=re.compile(r"\[\d+\.\d+\.\d+\]"))
            if fecha_elem:
                fecha_texto = fecha_elem.get_text()
                match = re.search(r"\[(\d+)\.(\d+)\.(\d+)\]", fecha_texto)
                if match:
                    dia, mes, año = match.groups()
                    fecha = f"{año}-{mes.zfill(2)}-{dia.zfill(2)}"

            # Buscar playlist
            playlist = []
            playlist_elem = contenedor.find("div") or contenedor.find("p")
            if playlist_elem:
                texto_playlist = playlist_elem.get_text()
                # Extraer canciones separadas por ::
                canciones = [c.strip() for c in texto_playlist.split("::") if c.strip()]
                playlist = canciones[:20]  # Limitar a 20 canciones

            # Buscar enlaces extra
            enlaces_extra = []
            enlaces_verdes = contenedor.find_all(
                "a", style=re.compile(r"color: #99cc00")
            )
            for enlace_verde in enlaces_verdes:
                texto = enlace_verde.get_text(strip=True)
                url = enlace_verde.get("href")
                if texto and url:
                    enlaces_extra.append({"text": texto, "url": url})

            return {
                "cover_image_url": cover_image_url,
                "fecha": fecha,
                "playlist": playlist,
                "enlaces_extra": enlaces_extra,
            }

        except Exception as e:
            print(f"    ❌ Error extrayendo info: {e}")
            return None

    def actualizar_episodio_en_bd(self, episodio_info):
        """Actualiza un episodio en la base de datos."""
        try:
            numero = episodio_info["numero"]

            # Buscar episodio en BD
            podcasts = self.db.get_all_podcasts()
            episodio_bd = None

            for p in podcasts:
                if p.get("program_number") == numero:
                    episodio_bd = p
                    break

            if episodio_bd:
                # Construir URL WordPress estimada
                wordpress_url = f"https://popcastingpop.com/episodio-{numero}/"

                # Actualizar información web
                self.db.update_web_info(
                    episodio_bd["id"],
                    wordpress_url,
                    episodio_info["info"].get("cover_image_url"),
                    json.dumps(episodio_info["info"].get("enlaces_extra", [])),
                    json.dumps(episodio_info["info"].get("playlist", [])),
                )

                print(f"  ✅ Episodio #{numero} actualizado en BD")
                return True
            else:
                print(f"  ❌ Episodio #{numero} no encontrado en BD")
                return False

        except Exception as e:
            print(f"  ❌ Error actualizando episodio #{numero}: {e}")
            return False

    def buscar_todos(self):
        """Busca todos los episodios faltantes en todas las páginas."""
        print("🔍 BUSCANDO EPISODIOS FALTANTES AUTOMÁTICAMENTE")
        print("=" * 60)

        episodios_encontrados = []

        for url in self.paginas_archivo:
            encontrados = self.buscar_episodios_en_pagina(url)
            episodios_encontrados.extend(encontrados)

        print("\n📊 RESUMEN DE BÚSQUEDA")
        print("-" * 40)
        print(f"Episodios encontrados: {len(episodios_encontrados)}")

        if episodios_encontrados:
            print("\n🔄 ACTUALIZANDO BASE DE DATOS")
            print("-" * 40)

            actualizados = 0
            for episodio in episodios_encontrados:
                if self.actualizar_episodio_en_bd(episodio):
                    actualizados += 1

            print(f"\n✅ {actualizados} episodios actualizados exitosamente")
        else:
            print("❌ No se encontraron episodios faltantes")

        # Mostrar episodios que aún faltan
        encontrados_numeros = [e["numero"] for e in episodios_encontrados]
        faltantes = [
            num for num in self.episodios_faltantes if num not in encontrados_numeros
        ]

        if faltantes:
            print(f"\n⚠️  Episodios que aún faltan: {', '.join(faltantes)}")
        else:
            print("\n🎉 ¡Todos los episodios faltantes han sido encontrados!")


def main():
    buscador = BuscadorEpisodiosFaltantes()
    buscador.buscar_todos()


if __name__ == "__main__":
    main()
