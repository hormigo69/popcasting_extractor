#!/usr/bin/env python3
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

Script para extraer los episodios 61, 62 y 63 de la página programas-anteriores-42-63.
"""

import json
import re

import requests
from bs4 import BeautifulSoup

from services.supabase_database import SupabaseDatabase


def extraer_episodios_61_62_63():
    """Extrae los episodios 61, 62 y 63 de la página específica."""
    print("🔍 EXTRAYENDO EPISODIOS 61, 62 Y 63")
    print("=" * 50)

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

        # Buscar el contenido de la página
        contenido = soup.get_text()

        # Extraer episodios específicos
        episodios_encontrados = []

        # Buscar episodio #61
        match_61 = re.search(
            r"programa #61.*?\[(\d+)\.(\d+)\.(\d+)\].*?<https://www\.ivoox\.com/popcasting061[^>]*>",
            contenido,
            re.DOTALL,
        )
        if match_61:
            dia, mes, año = match_61.groups()
            fecha_61 = f"{año}-{mes.zfill(2)}-{dia.zfill(2)}"

            # Buscar playlist del episodio 61
            playlist_61 = extraer_playlist_episodio(contenido, 61)

            episodios_encontrados.append(
                {
                    "numero": "61",
                    "fecha": fecha_61,
                    "playlist": playlist_61,
                    "url_ivoox": "https://www.ivoox.com/popcasting061-audios-mp3_rf_346644_1.html",
                }
            )
            print(f"✅ Episodio #61 encontrado - Fecha: {fecha_61}")

        # Buscar episodio #62
        match_62 = re.search(
            r"programa #62.*?\[(\d+)\.(\d+)\.(\d+)\].*?<https://www\.ivoox\.com/popcasting062[^>]*>",
            contenido,
            re.DOTALL,
        )
        if match_62:
            dia, mes, año = match_62.groups()
            fecha_62 = f"{año}-{mes.zfill(2)}-{dia.zfill(2)}"

            # Buscar playlist del episodio 62
            playlist_62 = extraer_playlist_episodio(contenido, 62)

            episodios_encontrados.append(
                {
                    "numero": "62",
                    "fecha": fecha_62,
                    "playlist": playlist_62,
                    "url_ivoox": "https://www.ivoox.com/popcasting062-audios-mp3_rf_346643_1.html",
                }
            )
            print(f"✅ Episodio #62 encontrado - Fecha: {fecha_62}")

        # Buscar episodio #63
        match_63 = re.search(
            r"programa #63.*?\[(\d+)\.(\d+)\.(\d+)\].*?<https://www\.ivoox\.com/popcasting063[^>]*>",
            contenido,
            re.DOTALL,
        )
        if match_63:
            dia, mes, año = match_63.groups()
            fecha_63 = f"{año}-{mes.zfill(2)}-{dia.zfill(2)}"

            # Buscar playlist del episodio 63
            playlist_63 = extraer_playlist_episodio(contenido, 63)

            episodios_encontrados.append(
                {
                    "numero": "63",
                    "fecha": fecha_63,
                    "playlist": playlist_63,
                    "url_ivoox": "https://www.ivoox.com/popcasting063-audios-mp3_rf_346642_1.html",
                }
            )
            print(f"✅ Episodio #63 encontrado - Fecha: {fecha_63}")

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
                            None,  # No tenemos imagen de portada
                            None,  # No tenemos enlaces extra
                            json.dumps(episodio["playlist"]),
                        )

                        print(f"  ✅ Episodio #{episodio['numero']} actualizado")
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


def extraer_playlist_episodio(contenido, numero_episodio):
    """Extrae la playlist de un episodio específico."""
    try:
        # Buscar la sección del episodio
        pattern = rf"programa #{numero_episodio}.*?\[.*?\](.*?)<https://www\.ivoox\.com/popcasting{numero_episodio:03d}[^>]*>"
        match = re.search(pattern, contenido, re.DOTALL)

        if match:
            texto_playlist = match.group(1).strip()
            # Extraer canciones separadas por ::
            canciones = [c.strip() for c in texto_playlist.split("::") if c.strip()]
            return canciones[:20]  # Limitar a 20 canciones

        return []

    except Exception as e:
        print(f"    ❌ Error extrayendo playlist del episodio #{numero_episodio}: {e}")
        return []


if __name__ == "__main__":
    extraer_episodios_61_62_63()
