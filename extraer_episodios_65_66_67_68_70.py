#!/usr/bin/env python3
"""
Script para extraer los episodios 65, 66, 67, 68 y 70 de la página programas-anteriores-64-91.
"""

import json

from services.supabase_database import SupabaseDatabase


def extraer_episodios_65_66_67_68_70():
    """Extrae los episodios 65, 66, 67, 68 y 70 con toda la información."""
    print("🔍 EXTRAYENDO EPISODIOS 65, 66, 67, 68 Y 70")
    print("=" * 60)

    # Información manual extraída de la página
    episodios_info = {
        "65": {
            "fecha": "2008-02-15",
            "playlist": [
                "adele · chasing pavements",
                "the duke spirit · the step and the walk",
                "furniture · brilliant mind",
                "jimmy scott · sycamore tree",
                "angelo badalamenti · laura palmer's theme",
                "black pony express · vera lynn",
                "cardinal · you've lost me there",
                "sven libaek · dark world",
                "henri salvador · adieu foulards, adieu madras",
                "kings have long arms (ft candie payne) · big umbrella",
            ],
            "enlaces_extra": [
                {"text": "the independent", "url": "#"},
                {"text": "les inrockuptibles", "url": "#"},
                {"text": "adam & joe bbc 6", "url": "#"},
                {"text": "trunk records", "url": "#"},
                {"text": "jimmy scott · sycamore trees", "url": "#"},
                {"text": "angelo badalamenti – laura palmer's theme", "url": "#"},
            ],
            "cover_image_url": None,
        },
        "66": {
            "fecha": "2008-03-01",
            "playlist": [
                "vashti bunyan · wishwanderer",
                "the mamas and the papas · honeymoon (no dough)",
                "the house of love · real animal",
                "cat power · sea of love",
                "phil phillips · sea of love",
                "marissa nadler · diamond heart",
                "lykke li · time flies",
                "robert crumb and his cheap suit serenaders · get a load of this",
                "yelle · amour du sol",
                "slumberparty · fantasy",
            ],
            "enlaces_extra": [{"text": "marissa nadler", "url": "#"}],
            "cover_image_url": None,
        },
        "67": {
            "fecha": "2008-03-15",
            "playlist": [
                "pale fountains · just a girl",
                "irene · by your side",
                "girlfrendo · make up",
                "the undertones · wednesday week",
                "dexys midnight runners · let's make this precious",
                "billy bragg · you woke up my neighbourhood",
                "sea urchins · pristine christine",
                "butcher boy · profit in your poetry",
                "arctic monkeys · fluorescent adolescent",
                "white town · taste of a girl",
                "les calamités · vélomoteur",
            ],
            "enlaces_extra": [
                {"text": "irene myspace", "url": "#"},
                {"text": "irene · by your side", "url": "#"},
                {"text": "butcher boy myspace", "url": "#"},
            ],
            "cover_image_url": None,
        },
        "68": {
            "fecha": "2008-04-01",
            "playlist": [
                "kool and the gang · fresh",
                "mink deville · venus of avenue d",
                "blondie · out in the streets",
                "the raindrops · let's go together",
                "carole king · it might as well rain until september",
                "darlene love · a fine, fine boy",
                "stone poneys · different drum",
                "charlie feathers · bottle to the baby",
                "yoko ono · walking on thin ice",
                "bobby womack · across 110th street",
            ],
            "enlaces_extra": [],
            "cover_image_url": None,
        },
        "70": {
            "fecha": "2008-05-01",
            "playlist": [
                "robert forster · if it rains",
                "laura cantrell · trains and boats and planes",
                "portishead · hunter",
                "wendy james · do you know what i'm saying",
                "henri salvador – dracula cha-cha-cha",
                "les paul & mary ford · tiger rag",
                "trini lopez · don't let the sun catch you cryin'",
                "jerry cole · george played",
                "silver apples · program",
                "madonna · she's not me",
            ],
            "enlaces_extra": [
                {"text": "laura cantrell myspace", "url": "#"},
                {"text": "portishead @ jools holland", "url": "#"},
            ],
            "cover_image_url": None,
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

    if actualizados == 5:
        print("🎉 ¡Todos los episodios 65, 66, 67, 68 y 70 actualizados exitosamente!")

    return actualizados


if __name__ == "__main__":
    extraer_episodios_65_66_67_68_70()
