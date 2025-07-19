#!/usr/bin/env python3
"""
Script para actualizar el episodio #60 con información manual extraída.
"""

import json

from services.supabase_database import SupabaseDatabase


def actualizar_episodio_60():
    """Actualiza el episodio #60 con la información manual extraída."""
    print("🔄 ACTUALIZANDO EPISODIO #60")
    print("=" * 40)

    # Inicializar base de datos
    db = SupabaseDatabase()

    # Información extraída manualmente del episodio #60
    info_episodio_60 = {
        "wordpress_url": "https://popcastingpop.com/episodio-60/",  # URL estimada
        "cover_image_url": "https://popcastingpop.com/wp-content/uploads/2023/08/aliccia.jpg?w=420",
        "audio_url": "https://www.ivoox.com/popcasting060-audios-mp3_rf_2710991_1.html",
        "fecha": "2007-12-01",
        "playlist": [
            "nancy & lee · you've lost that lovin' feeling",
            "ville valo & natalia avelon · summer wine",
            "raveonettes · dead sound",
            "slumber party · sooner or later",
            "rilo kiley · silver lining",
            "george harrison · maxine",
            "orquesta los guacamayos (juanito sánchez) · especial bugui",
            "the turtles · happy together",
            "ava leigh · burnin'",
            "duffy · rockferry",
            "françoise · hum! hum!",
            "ann lee · catches your love",
            "the korgis · everybody's got to learn sometime",
            "rufus wainwright · lost in tiergarten (supermayer remix)",
        ],
        "enlaces_extra": [
            {"text": "slumber party", "url": "http://www.myspace.com/slumberpartyband"},
            {
                "text": "the true story of the travelling wilburys",
                "url": "http://www.youtube.com/watch?v=sNEFSA7sKXA",
            },
            {
                "text": "el extraño viaje (baile de angelines)",
                "url": "http://es.youtube.com/watch?v=1L8b3fUcF9s",
            },
            {"text": "ava leigh", "url": "http://www.myspace.com/avaleigh"},
            {"text": "duffy", "url": "http://www.myspace.com/duffymyspace"},
            {
                "text": "swingin' mademoiselle vol I",
                "url": "http://spikedcandy.blog-city.com/swing_mademoiselle.htm",
            },
            {
                "text": "swingin' mademoiselle vol II",
                "url": "http://spikedcandy.blog-city.com/lets_swing_again.htm",
            },
        ],
    }

    try:
        # Buscar el episodio #60 en la base de datos
        podcasts = db.get_all_podcasts()
        episodio_60 = None

        for p in podcasts:
            if p.get("program_number") == "60":
                episodio_60 = p
                break

        if episodio_60:
            # Actualizar información web
            db.update_web_info(
                episodio_60["id"],
                info_episodio_60["wordpress_url"],
                info_episodio_60["cover_image_url"],
                json.dumps(info_episodio_60["enlaces_extra"]),
                json.dumps(info_episodio_60["playlist"]),
            )

            print("✅ Episodio #60 actualizado exitosamente")
            print(f"   - URL WordPress: {info_episodio_60['wordpress_url']}")
            print(f"   - Imagen de portada: {info_episodio_60['cover_image_url']}")
            print(f"   - Canciones: {len(info_episodio_60['playlist'])}")
            print(f"   - Enlaces extra: {len(info_episodio_60['enlaces_extra'])}")

        else:
            print("❌ Episodio #60 no encontrado en la base de datos")

    except Exception as e:
        print(f"❌ Error actualizando episodio #60: {e}")


if __name__ == "__main__":
    actualizar_episodio_60()
