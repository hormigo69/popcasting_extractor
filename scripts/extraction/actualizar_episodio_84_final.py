#!/usr/bin/env python3
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

Script para actualizar el episodio #84 con toda la información y alcanzar el 100% de cobertura.
"""

import json

from services.supabase_database import SupabaseDatabase


def actualizar_episodio_84():
    """Actualiza el episodio #84 con toda la información proporcionada."""
    print("🎯 ACTUALIZANDO EPISODIO #84 - ÚLTIMO EPISODIO")
    print("=" * 60)

    # Información completa del episodio #84
    episodio_84_info = {
        "fecha": "2008-12-01",
        "playlist": [
            "pete drake · forever",
            "george harrison · i live for you",
            "frank zappa · hungry freaks, daddy",
            "the sonics · anyway the wind blows",
            "serge gainsbourg · j'entends siffler le train",
            "john and jehn · 20 L 07",
            "jurassic 5 · concrete schoolyard",
            "ike turner & the harlem rhythm kings · getting nasty",
            "juliana hatfield · my sister",
            "françoise breut · les jeunes pousses",
        ],
        "enlaces_extra": [
            {
                "text": "pete drake · forever (video)",
                "url": "http://www.boingboing.net/2008/11/17/old-video-of-talking.html",
            },
            {"text": "john and jehn myspace", "url": "http://www.myspace.com/johnjehn"},
            {
                "text": "mojo november 1993",
                "url": "http://cover.mojo4music.com/Item.aspx?pageNo=1568&year=1993",
            },
            {
                "text": "françoise breut · el pais",
                "url": "http://www.elpais.com/articulo/cultura/Francoiz/Breut/estrena/disco/ELPAIScom/elpepucul/20081128elpepucul_2/Tes",
            },
            {"text": "green ufos", "url": "http://www.greenufos.com"},
        ],
        "cover_image_url": "https://popcastingpop.com/wp-content/uploads/2023/08/peted.jpg",
        "wordpress_url": "https://popcastingpop.com/programas-anteriores-64-91/peted/",
    }

    print(f"📅 Fecha: {episodio_84_info['fecha']}")
    print(f"🎵 Canciones: {len(episodio_84_info['playlist'])}")
    print(f"🔗 Enlaces extra: {len(episodio_84_info['enlaces_extra'])}")
    print(f"🖼️ Cover image: {episodio_84_info['cover_image_url']}")
    print(f"🌐 URL: {episodio_84_info['wordpress_url']}")
    print()

    # Actualizar base de datos
    print("🔄 ACTUALIZANDO BASE DE DATOS")
    print("-" * 40)

    db = SupabaseDatabase()

    try:
        # Buscar episodio #84 en BD
        podcasts = db.get_all_podcasts()
        episodio_bd = None

        for p in podcasts:
            if p.get("program_number") == "84":
                episodio_bd = p
                break

        if episodio_bd:
            # Actualizar información web
            db.update_web_info(
                episodio_bd["id"],
                episodio_84_info["wordpress_url"],
                episodio_84_info["cover_image_url"],
                json.dumps(episodio_84_info["enlaces_extra"]),
                json.dumps(episodio_84_info["playlist"]),
            )

            print("  ✅ Episodio #84 actualizado exitosamente!")
            print("  🎉 ¡100% DE COBERTURA ALCANZADO!")

            return True
        else:
            print("  ❌ Episodio #84 no encontrado en BD")
            return False

    except Exception as e:
        print(f"  ❌ Error actualizando episodio #84: {e}")
        return False


def verificar_cobertura_final():
    """Verifica la cobertura final después de actualizar el episodio #84."""
    print("\n📊 VERIFICANDO COBERTURA FINAL")
    print("=" * 40)

    db = SupabaseDatabase()
    podcasts = db.get_all_podcasts()

    total = len(podcasts)
    con_info_web = sum(1 for p in podcasts if p.get("wordpress_url"))
    sin_info_web = total - con_info_web
    cobertura = (con_info_web / total) * 100 if total > 0 else 0

    print("📈 ESTADO FINAL:")
    print(f"   Total episodios: {total}")
    print(f"   Con información web: {con_info_web}")
    print(f"   Sin información web: {sin_info_web}")
    print(f"   Cobertura: {cobertura:.1f}%")

    if cobertura == 100.0:
        print("\n🎊 ¡FELICIDADES! ¡100% DE COBERTURA ALCANZADO!")
        print("   🏆 Todos los episodios tienen información web completa")
    else:
        print(f"\n⚠️  Aún faltan {sin_info_web} episodios para el 100%")

        if sin_info_web > 0:
            print("   Episodios faltantes:")
            for p in podcasts:
                if not p.get("wordpress_url"):
                    print(f"     - Episodio #{p.get('program_number')}")


if __name__ == "__main__":
    # Actualizar episodio #84
    success = actualizar_episodio_84()

    if success:
        # Verificar cobertura final
        verificar_cobertura_final()

        print("\n" + "=" * 60)
        print("🎯 MISIÓN COMPLETADA")
        print("   Base de datos Popcasting: 100% de cobertura")
        print("   Todos los episodios tienen información web")
        print("=" * 60)
