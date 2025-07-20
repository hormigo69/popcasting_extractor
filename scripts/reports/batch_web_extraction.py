#!/usr/bin/env python3
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

Script para extraer información web de todos los episodios de Popcasting de forma masiva.
"""

import time

from services import database as db
from services.web_extractor import WebExtractor


def main():
    print("🚀 Iniciando extracción masiva de información web de Popcasting")
    print("=" * 60)

    # Inicializar base de datos
    db.initialize_database()

    # Obtener episodios sin información web
    podcasts = db.get_podcasts_without_web_info()
    total_episodes = len(podcasts)

    print(f"📊 Total de episodios a procesar: {total_episodes}")

    if total_episodes == 0:
        print("✅ Todos los episodios ya tienen información web")
        return

    # Inicializar extractor
    extractor = WebExtractor()

    # Estadísticas
    processed = 0
    errors = 0
    start_time = time.time()

    print("\n🔄 Procesando episodios...")
    print("-" * 60)

    for i, podcast in enumerate(podcasts, 1):
        try:
            print(
                f"[{i:3d}/{total_episodes}] 📄 Procesando episodio {podcast['program_number']} ({podcast['date']})"
            )

            # Buscar URL de WordPress
            wordpress_url = extractor._find_wordpress_url(podcast)

            if wordpress_url:
                # Extraer información de la página del episodio
                web_info = extractor._extract_episode_page_info(wordpress_url)

                # Actualizar base de datos
                db.update_web_info(
                    podcast_id=podcast["id"],
                    wordpress_url=wordpress_url,
                    cover_image_url=web_info.get("cover_image_url"),
                    web_extra_links=web_info.get("extra_links_json"),
                    web_playlist=web_info.get("playlist_json"),
                )

                print(f"    ✅ Éxito - URL: {wordpress_url}")
                processed += 1
            else:
                print("    ⚠️  No se encontró URL de WordPress")
                errors += 1

            # Pausa entre requests para ser respetuoso con el servidor
            time.sleep(extractor.delay_between_requests)

            # Mostrar progreso cada 10 episodios
            if i % 10 == 0:
                elapsed_time = time.time() - start_time
                avg_time_per_episode = elapsed_time / i
                remaining_episodes = total_episodes - i
                estimated_remaining_time = remaining_episodes * avg_time_per_episode

                print(
                    f"\n📈 Progreso: {i}/{total_episodes} ({i/total_episodes*100:.1f}%)"
                )
                print(f"⏱️  Tiempo transcurrido: {elapsed_time/60:.1f} min")
                print(
                    f"⏳ Tiempo estimado restante: {estimated_remaining_time/60:.1f} min"
                )
                print(f"✅ Éxitos: {processed}, ❌ Errores: {errors}")
                print("-" * 60)

        except KeyboardInterrupt:
            print("\n⚠️  Proceso interrumpido por el usuario")
            break
        except Exception as e:
            error_msg = f"Error procesando episodio {podcast['program_number']}: {e}"
            print(f"    ❌ {error_msg}")
            errors += 1
            continue

    # Estadísticas finales
    total_time = time.time() - start_time

    print("\n🎉 Extracción masiva completada!")
    print("=" * 60)
    print("📊 Estadísticas finales:")
    print(f"   Total episodios: {total_episodes}")
    print(f"   ✅ Éxitos: {processed}")
    print(f"   ❌ Errores: {errors}")
    print(f"   📈 Tasa de éxito: {processed/total_episodes*100:.1f}%")
    print(f"   ⏱️  Tiempo total: {total_time/60:.1f} minutos")
    print(f"   🚀 Promedio: {total_time/total_episodes:.1f} segundos por episodio")

    # Verificar estado final de la base de datos
    conn = db.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as total FROM podcasts")
    total_db = cursor.fetchone()["total"]
    cursor.execute(
        "SELECT COUNT(*) as with_web FROM podcasts WHERE wordpress_url IS NOT NULL"
    )
    with_web = cursor.fetchone()["with_web"]
    conn.close()

    print("\n💾 Estado de la base de datos:")
    print(f"   Total episodios en BD: {total_db}")
    print(f"   Con información web: {with_web}")
    print(f"   Porcentaje total: {with_web/total_db*100:.1f}%")


if __name__ == "__main__":
    main()
