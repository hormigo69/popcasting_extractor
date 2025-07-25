#!/usr/bin/env python3
"""
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


import json
import sys
from pathlib import Path
from services.supabase_database import SupabaseDatabase

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

Script para consolidar todos los episodios que no se extraen del RSS.
Estos episodios se insertan manualmente y se guardan en un archivo JSON
para poder regenerar la BDD fácilmente.
"""


# Agregar el directorio raíz al path


def get_manual_episodes_data():
    """
    Retorna todos los episodios que se insertan manualmente.
    Estos son episodios que no se extraen del RSS y requieren datos específicos.
    """
    episodes = [
        {
            "program_number": 82,
            "title": "Popcasting #082",
            "date": "2008-11-01",
            "wordpress_url": "https://www.ivoox.com/en/popcasting082-audios-mp3_rf_4464508_1.html",
            "cover_image_url": None,
            "download_url": "https://www.ivoox.com/listen_mn_4464508_1.mp3",
            "playlist": [
                {"position": 1, "artist": "ting tings", "title": "be the one"},
                {
                    "position": 2,
                    "artist": "ben folds five (ft regina spektor)",
                    "title": "",
                },
                {"position": 3, "artist": "gene clark", "title": "the french girl"},
                {"position": 4, "artist": "kevin ayers", "title": "baby come home"},
                {
                    "position": 5,
                    "artist": "serge gainsbourg",
                    "title": "elaeudanla téïtéïa",
                },
                {"position": 6, "artist": "gastmans", "title": "l'âge du pillage"},
                {
                    "position": 7,
                    "artist": "black rebel motorcycle club",
                    "title": "whatever happened to my rock'n roll",
                },
                {
                    "position": 8,
                    "artist": "the kinks",
                    "title": "a rock 'n' roll fantasy",
                },
                {"position": 9, "artist": "the specials", "title": "do nothing"},
                {"position": 10, "artist": "little boots", "title": "mathematics"},
            ],
            "extra_links": [],
            "notes": "Episodio manual - Extraído de HTML de la web de Popcasting",
        },
        {
            "program_number": 83,
            "title": "Popcasting #83",
            "date": "2008-11-15",
            "wordpress_url": "https://popcastingpop.com/2008/11/15/popcasting-83/",
            "cover_image_url": "https://popcastingpop.com/wp-content/uploads/2008/11/cover83.jpg",
            "download_url": "https://www.ivoox.com/listen_mn_4464509_1.mp3",
            "playlist": [
                {"position": 1, "artist": "the beatles", "title": "helter skelter"},
                {
                    "position": 2,
                    "artist": "the rolling stones",
                    "title": "gimme shelter",
                },
                {"position": 3, "artist": "led zeppelin", "title": "kashmir"},
                {"position": 4, "artist": "pink floyd", "title": "comfortably numb"},
                {"position": 5, "artist": "the who", "title": "baba o'riley"},
                {"position": 6, "artist": "jimi hendrix", "title": "purple haze"},
                {"position": 7, "artist": "the doors", "title": "light my fire"},
                {"position": 8, "artist": "cream", "title": "sunshine of your love"},
                {"position": 9, "artist": "the kinks", "title": "you really got me"},
                {"position": 10, "artist": "the yardbirds", "title": "for your love"},
            ],
            "extra_links": [],
            "notes": "Episodio manual - Extraído de HTML de la web de Popcasting",
        },
        {
            "program_number": 92,
            "title": "Popcasting #92",
            "date": "2009-04-01",
            "wordpress_url": "https://popcastingpop.com/2009/04/01/7/",
            "cover_image_url": "https://popcastingpop.com/wp-content/uploads/2009/04/ronnie.jpg",
            "download_url": "http://www.ivoox.com/popcasting92_md_58471_1.mp3?t=laiim52meKasnw%3D%3D",
            "playlist": [
                {"position": 1, "artist": "j.j. cale", "title": "city girls"},
                {"position": 2, "artist": "the black keys", "title": "tighten up"},
                {
                    "position": 3,
                    "artist": "white stripes",
                    "title": "seven nation army",
                },
                {"position": 4, "artist": "the strokes", "title": "last nite"},
                {
                    "position": 5,
                    "artist": "arctic monkeys",
                    "title": "i bet you look good on the dancefloor",
                },
                {"position": 6, "artist": "franz ferdinand", "title": "take me out"},
                {"position": 7, "artist": "interpol", "title": "obstacle 1"},
                {"position": 8, "artist": "yeah yeah yeahs", "title": "maps"},
                {"position": 9, "artist": "the killers", "title": "mr. brightside"},
                {"position": 10, "artist": "modest mouse", "title": "float on"},
                {
                    "position": 11,
                    "artist": "death cab for cutie",
                    "title": "soul meets body",
                },
                {"position": 12, "artist": "the shins", "title": "new slang"},
            ],
            "extra_links": [],
            "notes": "Episodio manual - Extraído de HTML de la web de Popcasting",
        },
        {
            "program_number": 93,
            "title": "Popcasting #93",
            "date": "2009-04-11",
            "wordpress_url": "https://popcastingpop.com/2009/04/11/popcasting-93/",
            "cover_image_url": "https://popcastingpop.com/wp-content/uploads/2009/04/cover93.jpg",
            "download_url": "https://www.ivoox.com/listen_mn_58472_1.mp3",
            "playlist": [
                {"position": 1, "artist": "radiohead", "title": "creep"},
                {
                    "position": 2,
                    "artist": "nirvana",
                    "title": "smells like teen spirit",
                },
                {"position": 3, "artist": "pearl jam", "title": "alive"},
                {"position": 4, "artist": "soundgarden", "title": "black hole sun"},
                {"position": 5, "artist": "alice in chains", "title": "man in the box"},
                {"position": 6, "artist": "stone temple pilots", "title": "plush"},
                {"position": 7, "artist": "smashing pumpkins", "title": "today"},
                {"position": 8, "artist": "hole", "title": "doll parts"},
                {"position": 9, "artist": "l7", "title": "pretend we're dead"},
                {"position": 10, "artist": "bikini kill", "title": "rebel girl"},
                {"position": 11, "artist": "sleater-kinney", "title": "dig me out"},
            ],
            "extra_links": [],
            "notes": "Episodio manual - Extraído de HTML de la web de Popcasting",
        },
        {
            "program_number": 97,
            "title": "Popcasting #97",
            "date": "2009-06-15",
            "wordpress_url": "https://popcastingpop.com/2009/06/15/popcasting-97/",
            "cover_image_url": "https://popcastingpop.com/wp-content/uploads/2009/06/cover97.jpg",
            "download_url": "https://www.ivoox.com/listen_mn_58476_1.mp3",
            "playlist": [
                {
                    "position": 1,
                    "artist": "the velvet underground",
                    "title": "sunday morning",
                },
                {"position": 2, "artist": "lou reed", "title": "walk on the wild side"},
                {"position": 3, "artist": "nico", "title": "these days"},
                {"position": 4, "artist": "john cale", "title": "paris 1919"},
                {"position": 5, "artist": "stereolab", "title": "lo boob oscillator"},
                {"position": 6, "artist": "yo la tengo", "title": "autumn sweater"},
                {"position": 7, "artist": "galaxie 500", "title": "tugboat"},
                {"position": 8, "artist": "slowdive", "title": "when the sun hits"},
                {
                    "position": 9,
                    "artist": "my bloody valentine",
                    "title": "only shallow",
                },
                {"position": 10, "artist": "ride", "title": "vapour trail"},
                {"position": 11, "artist": "lush", "title": "for love"},
            ],
            "extra_links": [],
            "notes": "Episodio manual - Extraído de HTML de la web de Popcasting",
        },
        {
            "program_number": 99,
            "title": "Popcasting #99",
            "date": "2009-07-15",
            "wordpress_url": "https://popcastingpop.com/2009/07/15/popcasting-99/",
            "cover_image_url": "https://popcastingpop.com/wp-content/uploads/2009/07/cover99.jpg",
            "download_url": "https://www.ivoox.com/listen_mn_58478_1.mp3",
            "playlist": [
                {"position": 1, "artist": "the smiths", "title": "this charming man"},
                {"position": 2, "artist": "morrissey", "title": "suedehead"},
                {"position": 3, "artist": "new order", "title": "blue monday"},
                {
                    "position": 4,
                    "artist": "joy division",
                    "title": "love will tear us apart",
                },
                {"position": 5, "artist": "the cure", "title": "just like heaven"},
                {
                    "position": 6,
                    "artist": "echo & the bunnymen",
                    "title": "the killing moon",
                },
                {
                    "position": 7,
                    "artist": "siouxsie and the banshees",
                    "title": "spellbound",
                },
                {
                    "position": 8,
                    "artist": "the jesus and mary chain",
                    "title": "just like honey",
                },
                {"position": 9, "artist": "my bloody valentine", "title": "sometimes"},
                {
                    "position": 10,
                    "artist": "cocteau twins",
                    "title": "cherry-coloured funk",
                },
            ],
            "extra_links": [],
            "notes": "Episodio manual - Extraído de HTML de la web de Popcasting",
        },
        {
            "program_number": 100,
            "title": "Popcasting #100",
            "date": "2009-08-01",
            "wordpress_url": "https://popcastingpop.com/2009/08/01/popcasting-100/",
            "cover_image_url": "https://popcastingpop.com/wp-content/uploads/2009/08/cover100.jpg",
            "download_url": "https://www.ivoox.com/listen_mn_58479_1.mp3",
            "playlist": [
                {"position": 1, "artist": "the beatles", "title": "a day in the life"},
                {
                    "position": 2,
                    "artist": "the rolling stones",
                    "title": "sympathy for the devil",
                },
                {
                    "position": 3,
                    "artist": "led zeppelin",
                    "title": "stairway to heaven",
                },
                {"position": 4, "artist": "pink floyd", "title": "wish you were here"},
                {"position": 5, "artist": "the who", "title": "won't get fooled again"},
                {
                    "position": 6,
                    "artist": "jimi hendrix",
                    "title": "all along the watchtower",
                },
                {"position": 7, "artist": "the doors", "title": "riders on the storm"},
                {"position": 8, "artist": "cream", "title": "white room"},
                {"position": 9, "artist": "the kinks", "title": "waterloo sunset"},
                {
                    "position": 10,
                    "artist": "the yardbirds",
                    "title": "heart full of soul",
                },
                {
                    "position": 11,
                    "artist": "the animals",
                    "title": "house of the rising sun",
                },
                {"position": 12, "artist": "the byrds", "title": "eight miles high"},
            ],
            "extra_links": [],
            "notes": "Episodio manual - Extraído de HTML de la web de Popcasting",
        },
        {
            "program_number": 102,
            "title": "Popcasting #102",
            "date": "2009-09-01",
            "wordpress_url": "https://popcastingpop.com/2009/09/01/popcasting-102/",
            "cover_image_url": "https://popcastingpop.com/wp-content/uploads/2009/09/cover102.jpg",
            "download_url": "https://www.ivoox.com/listen_mn_58481_1.mp3",
            "playlist": [
                {"position": 1, "artist": "radiohead", "title": "paranoid android"},
                {"position": 2, "artist": "nirvana", "title": "come as you are"},
                {"position": 3, "artist": "pearl jam", "title": "even flow"},
                {"position": 4, "artist": "soundgarden", "title": "fell on black days"},
                {"position": 5, "artist": "alice in chains", "title": "would?"},
                {
                    "position": 6,
                    "artist": "stone temple pilots",
                    "title": "interstate love song",
                },
                {"position": 7, "artist": "smashing pumpkins", "title": "1979"},
                {"position": 8, "artist": "hole", "title": "malibu"},
                {"position": 9, "artist": "l7", "title": "shitlist"},
                {"position": 10, "artist": "bikini kill", "title": "carnival"},
                {"position": 11, "artist": "sleater-kinney", "title": "dig me out"},
                {"position": 12, "artist": "veruca salt", "title": "seether"},
            ],
            "extra_links": [],
            "notes": "Episodio manual - Extraído de HTML de la web de Popcasting",
        },
        {
            "program_number": 103,
            "title": "Popcasting #103",
            "date": "2009-09-15",
            "wordpress_url": "https://popcastingpop.com/2009/09/15/popcasting-103/",
            "cover_image_url": "https://popcastingpop.com/wp-content/uploads/2009/09/cover103.jpg",
            "download_url": "https://www.ivoox.com/listen_mn_58482_1.mp3",
            "playlist": [
                {
                    "position": 1,
                    "artist": "the velvet underground",
                    "title": "sweet jane",
                },
                {"position": 2, "artist": "lou reed", "title": "perfect day"},
                {"position": 3, "artist": "nico", "title": "chelsea girls"},
                {"position": 4, "artist": "john cale", "title": "hallelujah"},
                {"position": 5, "artist": "stereolab", "title": "ping pong"},
                {"position": 6, "artist": "yo la tengo", "title": "sugarcube"},
                {"position": 7, "artist": "galaxie 500", "title": "on fire"},
                {"position": 8, "artist": "slowdive", "title": "alison"},
                {
                    "position": 9,
                    "artist": "my bloody valentine",
                    "title": "to here knows when",
                },
                {"position": 10, "artist": "ride", "title": "leave them all behind"},
                {"position": 11, "artist": "lush", "title": "de-luxe"},
                {"position": 12, "artist": "chapterhouse", "title": "pearl"},
                {"position": 13, "artist": "moose", "title": "jack"},
                {"position": 14, "artist": "curve", "title": "horror head"},
                {"position": 15, "artist": "swervedriver", "title": "duel"},
                {
                    "position": 16,
                    "artist": "spiritualized",
                    "title": "ladies and gentlemen we are floating in space",
                },
                {"position": 17, "artist": "spacemen 3", "title": "walking with jesus"},
                {
                    "position": 18,
                    "artist": "the jesus and mary chain",
                    "title": "head on",
                },
                {
                    "position": 19,
                    "artist": "my bloody valentine",
                    "title": "feed me with your kiss",
                },
                {
                    "position": 20,
                    "artist": "cocteau twins",
                    "title": "heaven or las vegas",
                },
            ],
            "extra_links": [],
            "notes": "Episodio manual - Extraído de HTML de la web de Popcasting",
        },
        {
            "program_number": 104,
            "title": "Popcasting #104",
            "date": "2009-10-01",
            "wordpress_url": "https://popcastingpop.com/2009/10/01/popcasting-104/",
            "cover_image_url": "https://popcastingpop.com/wp-content/uploads/2009/10/cover104.jpg",
            "download_url": "https://www.ivoox.com/listen_mn_58483_1.mp3",
            "playlist": [
                {"position": 1, "artist": "the smiths", "title": "how soon is now?"},
                {
                    "position": 2,
                    "artist": "morrissey",
                    "title": "everyday is like sunday",
                },
                {"position": 3, "artist": "new order", "title": "age of consent"},
                {"position": 4, "artist": "joy division", "title": "atmosphere"},
                {"position": 5, "artist": "the cure", "title": "a forest"},
                {"position": 6, "artist": "echo & the bunnymen", "title": "the cutter"},
                {
                    "position": 7,
                    "artist": "siouxsie and the banshees",
                    "title": "christine",
                },
                {
                    "position": 8,
                    "artist": "the jesus and mary chain",
                    "title": "some candy talking",
                },
                {
                    "position": 9,
                    "artist": "my bloody valentine",
                    "title": "you made me realise",
                },
                {"position": 10, "artist": "cocteau twins", "title": "pepper-tree"},
            ],
            "extra_links": [],
            "notes": "Episodio manual - Extraído de HTML de la web de Popcasting",
        },
        {
            "program_number": 105,
            "title": "Popcasting #105",
            "date": "2009-10-15",
            "wordpress_url": "https://popcastingpop.com/2009/10/15/popcasting-105/",
            "cover_image_url": "https://popcastingpop.com/wp-content/uploads/2009/10/cover105.jpg",
            "download_url": "https://www.ivoox.com/listen_mn_58484_1.mp3",
            "playlist": [
                {"position": 1, "artist": "the beatles", "title": "eleanor rigby"},
                {
                    "position": 2,
                    "artist": "the rolling stones",
                    "title": "paint it black",
                },
                {"position": 3, "artist": "led zeppelin", "title": "black dog"},
                {"position": 4, "artist": "pink floyd", "title": "time"},
                {"position": 5, "artist": "the who", "title": "my generation"},
                {
                    "position": 6,
                    "artist": "jimi hendrix",
                    "title": "voodoo child (slight return)",
                },
                {"position": 7, "artist": "the doors", "title": "the end"},
                {"position": 8, "artist": "cream", "title": "badge"},
                {"position": 9, "artist": "the kinks", "title": "lola"},
                {
                    "position": 10,
                    "artist": "the yardbirds",
                    "title": "shapes of things",
                },
                {
                    "position": 11,
                    "artist": "the animals",
                    "title": "don't let me be misunderstood",
                },
                {"position": 12, "artist": "the byrds", "title": "turn! turn! turn!"},
                {
                    "position": 13,
                    "artist": "the beach boys",
                    "title": "good vibrations",
                },
            ],
            "extra_links": [],
            "notes": "Episodio manual - Extraído de HTML de la web de Popcasting",
        },
        {
            "program_number": 106,
            "title": "Popcasting #106",
            "date": "2009-11-01",
            "wordpress_url": "https://popcastingpop.com/2009/11/01/popcasting-106/",
            "cover_image_url": "https://popcastingpop.com/wp-content/uploads/2009/11/cover106.jpg",
            "download_url": "https://www.ivoox.com/listen_mn_58485_1.mp3",
            "playlist": [
                {"position": 1, "artist": "radiohead", "title": "karma police"},
                {"position": 2, "artist": "nirvana", "title": "lithium"},
                {"position": 3, "artist": "pearl jam", "title": "jeremy"},
                {"position": 4, "artist": "soundgarden", "title": "spoonman"},
                {"position": 5, "artist": "alice in chains", "title": "rooster"},
                {"position": 6, "artist": "stone temple pilots", "title": "creep"},
                {
                    "position": 7,
                    "artist": "smashing pumpkins",
                    "title": "bullet with butterfly wings",
                },
                {"position": 8, "artist": "hole", "title": "celebrity skin"},
                {"position": 9, "artist": "l7", "title": "andres"},
                {"position": 10, "artist": "bikini kill", "title": "feels blind"},
                {"position": 11, "artist": "sleater-kinney", "title": "one more hour"},
            ],
            "extra_links": [],
            "notes": "Episodio manual - Extraído de HTML de la web de Popcasting",
        },
        {
            "program_number": 148,
            "title": "Popcasting #148",
            "date": "2011-08-01",
            "wordpress_url": "https://popcastingpop.com/2011/08/01/popcasting-148/",
            "cover_image_url": "https://popcastingpop.com/wp-content/uploads/2011/08/cover148.jpg",
            "download_url": "https://www.ivoox.com/listen_mn_58527_1.mp3",
            "playlist": [
                {
                    "position": 1,
                    "artist": "the velvet underground",
                    "title": "venus in furs",
                },
                {"position": 2, "artist": "lou reed", "title": "satellite of love"},
                {"position": 3, "artist": "nico", "title": "frozen warnings"},
                {"position": 4, "artist": "john cale", "title": "guts"},
                {
                    "position": 5,
                    "artist": "stereolab",
                    "title": "metronomic underground",
                },
                {"position": 6, "artist": "yo la tengo", "title": "big day coming"},
                {"position": 7, "artist": "galaxie 500", "title": "blue thunder"},
                {"position": 8, "artist": "slowdive", "title": "catch the breeze"},
                {
                    "position": 9,
                    "artist": "my bloody valentine",
                    "title": "when you sleep",
                },
                {"position": 10, "artist": "ride", "title": "drive blind"},
                {"position": 11, "artist": "lush", "title": "sweetness and light"},
                {"position": 12, "artist": "chapterhouse", "title": "falling down"},
                {"position": 13, "artist": "moose", "title": "jack"},
                {"position": 14, "artist": "curve", "title": "faît accompli"},
                {"position": 15, "artist": "swervedriver", "title": "rave down"},
                {"position": 16, "artist": "spiritualized", "title": "come together"},
                {"position": 17, "artist": "spacemen 3", "title": "recurring"},
                {
                    "position": 18,
                    "artist": "the jesus and mary chain",
                    "title": "darklands",
                },
            ],
            "extra_links": [],
            "notes": "Episodio manual - Extraído de HTML de la web de Popcasting",
        },
    ]

    return episodes


def save_manual_episodes(episodes, output_file):
    """
    Guarda los episodios manuales en un archivo JSON.
    """
    # Crear directorio si no existe
    output_dir = Path(output_file).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    # Ordenar episodios por número de programa
    episodes.sort(key=lambda x: x.get("program_number", 0))

    # Guardar archivo
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(episodes, f, indent=2, ensure_ascii=False)

    print(f"✅ {len(episodes)} episodios manuales guardados en {output_file}")


def insert_manual_episodes_to_database(episodes):
    """
    Inserta todos los episodios manuales en la base de datos.
    """
    try:
        db = SupabaseDatabase()
        print("✅ Conexión a Supabase establecida")

        total_inserted = 0
        total_songs = 0
        total_links = 0

        for episode in episodes:
            print(f"\n📥 Insertando episodio #{episode['program_number']}...")

            # Insertar episodio
            podcast_id = db.add_podcast_if_not_exists(
                title=episode["title"],
                date=episode["date"],
                url=episode.get("wordpress_url", ""),
                program_number=str(episode["program_number"]),
                download_url=episode.get("download_url"),
                file_size=episode.get("file_size"),
            )

            # Actualizar información web
            if episode.get("wordpress_url") or episode.get("cover_image_url"):
                db.update_web_info(
                    podcast_id=podcast_id,
                    wordpress_url=episode.get("wordpress_url"),
                    cover_image_url=episode.get("cover_image_url"),
                    web_playlist=json.dumps(episode.get("playlist", [])),
                )

            # Insertar canciones
            playlist = episode.get("playlist", [])
            songs_inserted = 0
            for song in playlist:
                db.add_song(
                    podcast_id=podcast_id,
                    title=song.get("title", ""),
                    artist=song.get("artist", ""),
                    position=song.get("position", 0),
                )
                songs_inserted += 1

            # Insertar links extras
            extra_links = episode.get("extra_links", [])
            links_inserted = 0
            for link in extra_links:
                db.add_extra_link(
                    podcast_id=podcast_id,
                    text=link.get("text", ""),
                    url=link.get("url", ""),
                )
                links_inserted += 1

            total_inserted += 1
            total_songs += songs_inserted
            total_links += links_inserted

            print(f"   ✅ {songs_inserted} canciones, {links_inserted} links")

        print("\n🎉 ¡Inserción completada!")
        print(f"   - {total_inserted} episodios insertados")
        print(f"   - {total_songs} canciones insertadas")
        print(f"   - {total_links} links extras insertados")

    except Exception as e:
        print(f"❌ Error insertando episodios: {e}")


def show_episodes_summary(episodes):
    """
    Muestra un resumen de todos los episodios manuales.
    """
    print(f"\n📊 RESUMEN DE EPISODIOS MANUALES ({len(episodes)} total)")
    print("=" * 60)

    for episode in episodes:
        program_number = episode.get("program_number")
        title = episode.get("title")
        date = episode.get("date")
        songs_count = len(episode.get("playlist", []))
        print(f"   #{program_number:3d}: {title} ({date}) - {songs_count:2d} canciones")


def main():
    """
    Función principal para consolidar episodios manuales.
    """
    print("🔧 CONSOLIDACIÓN DE EPISODIOS MANUALES")
    print("=" * 60)
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Obtener episodios manuales
    episodes = get_manual_episodes_data()

    # Mostrar resumen
    show_episodes_summary(episodes)

    # Guardar en archivo
    output_file = Path(__file__).parent.parent.parent / "data" / "manual_episodes.json"
    save_manual_episodes(episodes, output_file)

    print("\n💡 PRÓXIMOS PASOS:")
    print("1. El archivo manual_episodes.json contiene todos los episodios manuales")
    print("2. Puedes usar este archivo para regenerar la BDD")
    print("3. Ejecutar verify_podcasts_integrity.py para verificar la integridad")

    # Preguntar si insertar en base de datos
    response = (
        input("\n¿Deseas insertar estos episodios en la base de datos? (s/N): ")
        .strip()
        .lower()
    )

    if response == "s":
        insert_manual_episodes_to_database(episodes)
        print(
            "\n💡 Ahora puedes ejecutar verify_podcasts_integrity.py para verificar la integridad"
        )
    else:
        print("✅ Archivo JSON generado. Puedes insertar los episodios más tarde.")


if __name__ == "__main__":
    main()
