#!/usr/bin/env python3
"""
Script final para extraer los episodios 61, 62 y 63 con toda la información.
"""

import json

import requests
from bs4 import BeautifulSoup

from services.supabase_database import SupabaseDatabase


def extraer_episodios_61_62_63_final():
    """Extrae los episodios 61, 62 y 63 con toda la información."""
    print("🔍 EXTRAYENDO EPISODIOS 61, 62 Y 63 (FINAL)")
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
        BeautifulSoup(response.content, "html.parser")

        # Información manual extraída de la página
        episodios_info = {
            "61": {
                "fecha": "2007-12-15",
                "playlist": [
                    "slade · merry xmas everybody",
                    "sally shapiro · anorak christmas",
                    "the coctails · first snowfall",
                    "teri summers and the librettos · seasons greetings",
                    "the waikikis · white christmas",
                    "milton de lugg and the little eskimos · hooray for santy claus",
                    "the orioles · what are you doing new years eve",
                    "billy childish · christmas 1979",
                    "stafronn hakon · do they know it's christmas time",
                    "booker t & the mg's · jingle bells",
                    "joni mitchell · river",
                    "the waitresses · christmas wrapping",
                ],
                "enlaces_extra": [
                    {
                        "text": "wfmu's beware of the blog · american song poem mp3s",
                        "url": "http://blog.wfmu.org/freeform/2005/07/american_song_p.html#more",
                    },
                    {
                        "text": "american song-poem christmas",
                        "url": "http://www.amazon.com/American-Song-Poem-Christmas-Various-Artists/dp/B0000AYLIO",
                    },
                    {"text": "song poem music", "url": "http://www.songpoemmusic.com/"},
                    {
                        "text": "flowering toilet · xmas 2007",
                        "url": "http://floweringtoilet.blogspot.com/2007/11/x-mas-2007.html",
                    },
                    {
                        "text": "santa claus conquers the martians",
                        "url": "http://www.archive.org/details/santa_claus_conquers_the_martians",
                    },
                ],
                "cover_image_url": "https://popcastingpop.com/wp-content/uploads/2023/08/joni.jpg",
            },
            "62": {
                "fecha": "2008-01-01",
                "playlist": [
                    "lykke li · little bit",
                    "hot chip · ready for the floor",
                    "jackie brenston & his delta cats · rocket 88",
                    "amy winehouse · cupid",
                    "lily allen · don't get me wrong",
                    "the sundays · i kicked a boy",
                    "etienne daho · duel au soleil",
                    "rachel sweet · lover's lane",
                    "dominique a · l'endermonde",
                    "winter family · garden",
                    "simone white · christmas makes me blue",
                    "tracey thorn · king's cross (hot chip remix)",
                ],
                "enlaces_extra": [
                    {
                        "text": "lykke li myspace/video",
                        "url": "http://www.myspace.com/lykkeli",
                    },
                    {
                        "text": "winter family",
                        "url": "http://www.myspace.com/winterfamily",
                    },
                    {
                        "text": "simone white myspace",
                        "url": "http://www.myspace.com/simonewhite",
                    },
                    {
                        "text": "simone white · christmas makes me blue (video)",
                        "url": "http://www.dailymotion.com/tag/white/video/x3r4gq_simone-white-christmas-makes-me-blu_music",
                    },
                    {"text": "fluo kids", "url": "http://fluokids.blogspot.com/"},
                ],
                "cover_image_url": "https://popcastingpop.com/wp-content/uploads/2023/08/lykke.jpg",
            },
            "63": {
                "fecha": "2008-01-15",
                "playlist": [
                    "sibylle baier · tonight",
                    "jim white · jailbird",
                    "edwyn collins · one track mind",
                    "the smiths · please, please, please let me get what i want",
                    "the go-betweens · open invitation",
                    "saint etienne · say it to the rain",
                    "lionel belasco · las palmas de maracaibo",
                    "alizée · fifty-sixty",
                    "girls aloud · call the shots",
                    "angie care · your mind",
                ],
                "enlaces_extra": [],
                "cover_image_url": "https://popcastingpop.com/wp-content/uploads/2023/08/jimw.jpg",
            },
        }

        # Actualizar base de datos
        print("🔄 ACTUALIZANDO BASE DE DATOS")
        print("-" * 40)

        db = SupabaseDatabase()
        actualizados = 0

        for numero, info in episodios_info.items():
            try:
                # Buscar episodio en BD
                podcasts = db.get_all_podcasts()
                episodio_bd = None

                for p in podcasts:
                    if p.get("program_number") == numero:
                        episodio_bd = p
                        break

                if episodio_bd:
                    # Construir URL WordPress estimada
                    wordpress_url = f"https://popcastingpop.com/episodio-{numero}/"

                    # Actualizar información web
                    db.update_web_info(
                        episodio_bd["id"],
                        wordpress_url,
                        info["cover_image_url"],
                        json.dumps(info["enlaces_extra"]),
                        json.dumps(info["playlist"]),
                    )

                    print(f"  ✅ Episodio #{numero} actualizado")
                    print(f"     - Fecha: {info['fecha']}")
                    print(f"     - Canciones: {len(info['playlist'])}")
                    print(f"     - Enlaces extra: {len(info['enlaces_extra'])}")
                    actualizados += 1
                else:
                    print(f"  ❌ Episodio #{numero} no encontrado en BD")

            except Exception as e:
                print(f"  ❌ Error actualizando episodio #{numero}: {e}")

        print("\n📊 RESUMEN")
        print("-" * 20)
        print(f"Episodios actualizados: {actualizados}")

        if actualizados == 3:
            print("🎉 ¡Todos los episodios 61, 62 y 63 actualizados exitosamente!")

    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    extraer_episodios_61_62_63_final()
