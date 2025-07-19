#!/usr/bin/env python3
"""
Script mejorado para extraer los episodios 61, 62 y 63 de la página programas-anteriores-42-63.
"""

import json
import re

import requests
from bs4 import BeautifulSoup

from services.supabase_database import SupabaseDatabase


def extraer_episodios_61_62_63_mejorado():
    """Extrae los episodios 61, 62 y 63 con la estructura HTML real."""
    print("🔍 EXTRAYENDO EPISODIOS 61, 62 Y 63 (MEJORADO)")
    print("=" * 60)

    url = "https://popcastingpop.com/programas-anteriores-42-63/"

    try:
        # Hacer la petición
        session = requests.Session()
        session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
            }
        )

        response = session.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        episodios_encontrados = []

        # Buscar episodio #61
        print("🔍 Buscando episodio #61...")
        episodio_61 = extraer_episodio_especifico(
            soup,
            "61",
            "https://www.ivoox.com/popcasting061-audios-mp3_rf_4452767_1.html",
        )
        if episodio_61:
            episodios_encontrados.append(episodio_61)
            print(f"✅ Episodio #61 encontrado - Fecha: {episodio_61['fecha']}")

        # Buscar episodio #62
        print("🔍 Buscando episodio #62...")
        episodio_62 = extraer_episodio_especifico(
            soup,
            "62",
            "https://www.ivoox.com/popcasting062-audios-mp3_rf_4452772_1.html",
        )
        if episodio_62:
            episodios_encontrados.append(episodio_62)
            print(f"✅ Episodio #62 encontrado - Fecha: {episodio_62['fecha']}")

        # Buscar episodio #63
        print("🔍 Buscando episodio #63...")
        episodio_63 = extraer_episodio_especifico(
            soup,
            "63",
            "https://www.ivoox.com/popcasting063-audios-mp3_rf_4452780_1.html",
        )
        if episodio_63:
            episodios_encontrados.append(episodio_63)
            print(f"✅ Episodio #63 encontrado - Fecha: {episodio_63['fecha']}")

        # Actualizar base de datos
        if episodios_encontrados:
            print("\n🔄 ACTUALIZANDO BASE DE DATOS")
            print("-" * 40)

            db = SupabaseDatabase()
            actualizados = 0

            for episodio in episodios_encontrados:
                try:
                    # Buscar episodio en BD
                    podcasts = db.get_all_podcasts()
                    episodio_bd = None

                    for p in podcasts:
                        if p.get("program_number") == episodio["numero"]:
                            episodio_bd = p
                            break

                    if episodio_bd:
                        # Construir URL WordPress estimada
                        wordpress_url = (
                            f"https://popcastingpop.com/episodio-{episodio['numero']}/"
                        )

                        # Actualizar información web
                        db.update_web_info(
                            episodio_bd["id"],
                            wordpress_url,
                            episodio.get("cover_image_url"),
                            json.dumps(episodio.get("enlaces_extra", [])),
                            json.dumps(episodio.get("playlist", [])),
                        )

                        print(f"  ✅ Episodio #{episodio['numero']} actualizado")
                        print(f"     - Canciones: {len(episodio.get('playlist', []))}")
                        print(
                            f"     - Enlaces extra: {len(episodio.get('enlaces_extra', []))}"
                        )
                        actualizados += 1
                    else:
                        print(
                            f"  ❌ Episodio #{episodio['numero']} no encontrado en BD"
                        )

                except Exception as e:
                    print(
                        f"  ❌ Error actualizando episodio #{episodio['numero']}: {e}"
                    )

            print("\n📊 RESUMEN")
            print("-" * 20)
            print(f"Episodios encontrados: {len(episodios_encontrados)}")
            print(f"Episodios actualizados: {actualizados}")

        else:
            print("❌ No se encontraron los episodios 61, 62 o 63")

    except Exception as e:
        print(f"❌ Error accediendo a {url}: {e}")


def extraer_episodio_especifico(soup, numero, url_ivoox):
    """Extrae información de un episodio específico."""
    try:
        # Buscar el enlace del episodio
        enlace = soup.find("a", href=url_ivoox)
        if not enlace:
            return None

        # Buscar el contenedor del episodio
        contenedor = enlace.find_parent("div")
        if not contenedor:
            contenedor = enlace.parent

        # Buscar imagen de portada
        cover_image_url = None
        img = contenedor.find("img", {"data-orig-file": True})
        if img:
            cover_image_url = img.get("data-orig-file")

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
        playlist_elem = contenedor.find("div")
        if playlist_elem:
            texto_playlist = playlist_elem.get_text()
            # Extraer canciones separadas por ::
            canciones = [c.strip() for c in texto_playlist.split("::") if c.strip()]
            playlist = canciones[:20]  # Limitar a 20 canciones

        # Buscar enlaces extra
        enlaces_extra = []
        enlaces_verdes = contenedor.find_all("a", style=re.compile(r"color: #99cc00"))
        for enlace_verde in enlaces_verdes:
            texto = enlace_verde.get_text(strip=True)
            url = enlace_verde.get("href")
            if texto and url:
                enlaces_extra.append({"text": texto, "url": url})

        return {
            "numero": numero,
            "fecha": fecha,
            "cover_image_url": cover_image_url,
            "playlist": playlist,
            "enlaces_extra": enlaces_extra,
            "url_ivoox": url_ivoox,
        }

    except Exception as e:
        print(f"    ❌ Error extrayendo episodio #{numero}: {e}")
        return None


if __name__ == "__main__":
    extraer_episodios_61_62_63_mejorado()
