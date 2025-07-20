#!/usr/bin/env python3
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

Script para procesar URLs manuales de episodios faltantes finales.
Lee el archivo episodios_faltantes_actualizado.txt y actualiza la base de datos.
"""

from datetime import datetime

from services.supabase_database import SupabaseDatabase
from services.web_extractor import WebExtractor


def procesar_urls_manuales():
    """Procesa las URLs manuales de episodios faltantes."""
    print("🔄 PROCESANDO URLs MANUALES FINALES")
    print("=" * 50)

    # Inicializar
    db = SupabaseDatabase()
    web_extractor = WebExtractor()

    # Leer archivo de episodios faltantes
    try:
        with open("episodios_faltantes_actualizado.txt", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ No se encontró el archivo 'episodios_faltantes_actualizado.txt'")
        return

    # Extraer líneas con URLs
    lines = content.split("\n")
    episodios_a_procesar = []

    for line in lines:
        if "|" in line and "Episodio #" in line:
            parts = line.split("|")
            if len(parts) >= 5:
                numero = parts[0].strip().replace("Episodio #", "").strip()
                titulo = parts[1].strip()
                fecha = parts[2].strip()
                url_rss = parts[3].strip()
                url_web = parts[4].strip()

                if url_web and url_web != "":
                    episodios_a_procesar.append(
                        {
                            "numero": numero,
                            "titulo": titulo,
                            "fecha": fecha,
                            "url_rss": url_rss,
                            "url_web": url_web,
                        }
                    )

    if not episodios_a_procesar:
        print("⚠️  No se encontraron URLs web para procesar")
        print("   Asegúrate de haber añadido las URLs en el archivo")
        return

    print(f"📋 Encontrados {len(episodios_a_procesar)} episodios con URLs web")
    print()

    # Procesar cada episodio
    exitosos = 0
    errores = 0

    for episodio in episodios_a_procesar:
        try:
            print(f"🔄 Procesando episodio #{episodio['numero']}...")

            # Extraer información web
            info_web = web_extractor._extract_episode_page_info(episodio["url_web"])

            if info_web:
                # Buscar episodio en la base de datos
                podcasts = db.get_all_podcasts()
                episodio_db = None

                for p in podcasts:
                    if p.get("program_number") == episodio["numero"]:
                        episodio_db = p
                        break

                if episodio_db:
                    # Actualizar información web
                    db.update_web_info(
                        episodio_db["id"],
                        episodio["url_web"],
                        info_web.get("cover_image_url"),
                        info_web.get("extra_links"),
                        info_web.get("playlist_json"),
                    )

                    print(f"  ✅ Episodio #{episodio['numero']} actualizado")
                    exitosos += 1
                else:
                    print(f"  ❌ Episodio #{episodio['numero']} no encontrado en BD")
                    errores += 1
            else:
                print(f"  ❌ No se pudo extraer información de {episodio['url_web']}")
                errores += 1

        except Exception as e:
            print(f"  ❌ Error procesando episodio #{episodio['numero']}: {e}")
            errores += 1

        print()

    # Resumen final
    print("📊 RESUMEN FINAL")
    print("-" * 30)
    print(f"Episodios procesados exitosamente: {exitosos}")
    print(f"Errores: {errores}")
    print(f"Total: {exitosos + errores}")

    if exitosos > 0:
        print(f"\n🎉 ¡{exitosos} episodios actualizados!")
        print("   La cobertura de la base de datos ha mejorado.")

    print(f"\n📅 Proceso completado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    procesar_urls_manuales()
