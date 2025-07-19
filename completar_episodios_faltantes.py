#!/usr/bin/env python3
"""
Script para completar la información web de episodios faltantes.
Lee el archivo episodios_faltantes.txt y extrae información de las URLs encontradas manualmente.
"""

import re
import time

from services import database as db
from services.web_extractor import WebExtractor


def parse_episodios_faltantes():
    """
    Lee el archivo episodios_faltantes.txt y extrae las URLs manuales.
    """
    episodios = []

    try:
        with open("episodios_faltantes.txt", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()

            # Saltar líneas vacías y comentarios
            if not line or line.startswith("#") or line.startswith("="):
                continue

            # Buscar líneas con formato: ID: X | Número: Y | Fecha: Z | Título: W | URL_MANUAL: V
            match = re.match(
                r"ID:\s*(\d+)\s*\|\s*Número:\s*([^|]+)\s*\|\s*Fecha:\s*([^|]+)\s*\|\s*Título:\s*([^|]+)\s*\|\s*URL_MANUAL:\s*(.*)",
                line,
            )

            if match:
                episode_id = int(match.group(1))
                numero = match.group(2).strip()
                fecha = match.group(3).strip()
                titulo = match.group(4).strip()
                url_manual = match.group(5).strip()

                if url_manual and url_manual != "":
                    episodios.append(
                        {
                            "id": episode_id,
                            "numero": numero,
                            "fecha": fecha,
                            "titulo": titulo,
                            "url": url_manual,
                        }
                    )

        return episodios

    except FileNotFoundError:
        print("❌ No se encontró el archivo episodios_faltantes.txt")
        return []
    except Exception as e:
        print(f"❌ Error leyendo el archivo: {e}")
        return []


def procesar_episodios_manuales(episodios):
    """
    Procesa los episodios con URLs manuales y extrae su información web.
    """
    if not episodios:
        print("⚠️  No hay episodios con URLs manuales para procesar")
        return

    print(f"🚀 Procesando {len(episodios)} episodios con URLs manuales")
    print("=" * 60)

    # Inicializar base de datos y extractor
    db.initialize_database()
    extractor = WebExtractor()

    processed = 0
    errors = 0

    for i, episodio in enumerate(episodios, 1):
        try:
            print(
                f"[{i:2d}/{len(episodios)}] 📄 Procesando episodio {episodio['numero']} ({episodio['fecha']})"
            )
            print(f"    URL: {episodio['url']}")

            # Verificar que la URL es válida
            if not episodio["url"].startswith("http"):
                print(f"    ❌ URL inválida: {episodio['url']}")
                errors += 1
                continue

            # Extraer información de la página del episodio
            web_info = extractor._extract_episode_page_info(episodio["url"])

            if web_info:
                # Actualizar base de datos
                db.update_web_info(
                    podcast_id=episodio["id"],
                    wordpress_url=episodio["url"],
                    cover_image_url=web_info.get("cover_image_url"),
                    web_extra_links=web_info.get("extra_links_json"),
                    web_playlist=web_info.get("playlist_json"),
                )

                print(
                    f"    ✅ Éxito - Imagen: {web_info.get('cover_image_url', 'No encontrada')}"
                )
                processed += 1
            else:
                print("    ⚠️  No se pudo extraer información de la página")
                errors += 1

            # Pausa entre requests
            time.sleep(extractor.delay_between_requests)

        except Exception as e:
            print(f"    ❌ Error: {e}")
            errors += 1
            continue

    # Estadísticas finales
    print("\n🎉 Procesamiento completado!")
    print("=" * 60)
    print("📊 Estadísticas:")
    print(f"   Total episodios: {len(episodios)}")
    print(f"   ✅ Éxitos: {processed}")
    print(f"   ❌ Errores: {errors}")
    print(f"   📈 Tasa de éxito: {processed/len(episodios)*100:.1f}%")


def verificar_estado_final():
    """
    Verifica el estado final de la base de datos después del procesamiento.
    """
    conn = db.get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) as total FROM podcasts")
    total = cursor.fetchone()["total"]

    cursor.execute(
        "SELECT COUNT(*) as with_web FROM podcasts WHERE wordpress_url IS NOT NULL"
    )
    with_web = cursor.fetchone()["with_web"]

    cursor.execute(
        "SELECT COUNT(*) as with_cover FROM podcasts WHERE cover_image_url IS NOT NULL"
    )
    with_cover = cursor.fetchone()["with_cover"]

    conn.close()

    print("\n💾 Estado final de la base de datos:")
    print(f"   Total episodios: {total}")
    print(f"   Con wordpress_url: {with_web}")
    print(f"   Con cover_image_url: {with_cover}")
    print(f"   Porcentaje total: {with_web/total*100:.1f}%")


def main():
    print("🔍 Completando episodios faltantes con URLs manuales")
    print("=" * 60)

    # Leer episodios con URLs manuales
    episodios = parse_episodios_faltantes()

    if not episodios:
        print("❌ No se encontraron episodios con URLs manuales")
        print("💡 Asegúrate de haber completado el archivo episodios_faltantes.txt")
        return

    # Procesar episodios
    procesar_episodios_manuales(episodios)

    # Verificar estado final
    verificar_estado_final()

    print("\n✅ Proceso completado!")
    print(
        "💡 Si quedan episodios sin procesar, revisa las URLs en episodios_faltantes.txt"
    )


if __name__ == "__main__":
    main()
