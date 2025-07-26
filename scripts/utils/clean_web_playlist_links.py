#!/usr/bin/env python3
"""
Script para limpiar enlaces guardados incorrectamente como canciones en web_playlist
y verificar que web_songs_count coincida con el número real de canciones.

Este script:
1. Busca en web_playlist canciones que son enlaces (URLs)
2. Elimina esas canciones de la playlist
3. Actualiza web_songs_count con el número correcto
4. Verifica la coherencia entre web_playlist y web_songs_count
"""

import json
import os
import re
import sys
from typing import Any
from urllib.parse import urlparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.supabase_database import SupabaseDatabase


def is_url(text: str) -> bool:
    """
    Verifica si un texto es una URL válida.
    """
    if not text or not isinstance(text, str):
        return False

    # Patrones comunes de URLs que se han guardado como canciones
    url_patterns = [
        r"^https?://",  # URLs HTTP/HTTPS
        r"^//",  # URLs relativas
        r"^www\.",  # URLs que empiezan con www
        r"\.mp3$",  # Archivos MP3
        r"\.wav$",  # Archivos WAV
        r"\.html$",  # Archivos HTML
        r"\.php$",  # Archivos PHP
        r"ivoox\.com",  # Dominio iVoox
        r"popcasting",  # Palabra clave popcasting
    ]

    text_lower = text.lower().strip()

    # Verificar patrones
    for pattern in url_patterns:
        if re.search(pattern, text_lower):
            return True

    # Verificar si es una URL válida
    try:
        result = urlparse(text)
        return bool(result.scheme and result.netloc)
    except Exception:
        pass

    return False


def clean_playlist(playlist: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Limpia una playlist eliminando canciones que son enlaces.
    """
    if not playlist or not isinstance(playlist, list):
        return []

    cleaned_playlist = []
    removed_count = 0

    for song in playlist:
        if not isinstance(song, dict):
            continue

        artist = song.get("artist", "")
        title = song.get("title", "")

        # Verificar si el artista o título son URLs
        if is_url(artist) or is_url(title):
            removed_count += 1
            print(f"      🗑️  Eliminando canción con enlace: {artist} - {title}")
            continue

        # Verificar si el título está vacío o es muy corto (posible enlace)
        if not title or len(title.strip()) < 2:
            removed_count += 1
            print(f"      🗑️  Eliminando canción con título vacío: {artist} - {title}")
            continue

        # Verificar si contiene palabras clave de enlaces
        if any(
            keyword in title.lower()
            for keyword in ["http", "www", ".com", ".mp3", "ivoox"]
        ):
            removed_count += 1
            print(
                f"      🗑️  Eliminando canción con palabras clave de enlace: {artist} - {title}"
            )
            continue

        cleaned_playlist.append(song)

    if removed_count > 0:
        print(f"      ✅ Eliminadas {removed_count} canciones con enlaces")

    return cleaned_playlist


def verify_web_songs_count_coherence(db: SupabaseDatabase) -> dict[str, Any]:
    """
    Verifica la coherencia entre web_playlist y web_songs_count en todos los episodios.
    """
    print("🔍 Verificando coherencia entre web_playlist y web_songs_count...")

    try:
        # Obtener todos los episodios con web_playlist
        response = (
            db.client.table("podcasts")
            .select("id, program_number, title, web_playlist, web_songs_count")
            .not_.is_("web_playlist", "null")
            .execute()
        )

        episodes = response.data
        print(f"📊 Analizando {len(episodes)} episodios con web_playlist...")

        results = {
            "total_episodes": len(episodes),
            "coherent_episodes": 0,
            "incoherent_episodes": 0,
            "cleaned_episodes": 0,
            "errors": [],
            "details": [],
        }

        for episode in episodes:
            episode_id = episode["id"]
            program_number = episode["program_number"]
            title = episode["title"]
            web_playlist = episode["web_playlist"]
            web_songs_count = episode["web_songs_count"]

            try:
                # Parsear web_playlist
                playlist = json.loads(web_playlist)
                if not isinstance(playlist, list):
                    results["errors"].append(
                        {
                            "program_number": program_number,
                            "title": title,
                            "error": "web_playlist no es una lista",
                        }
                    )
                    continue

                # Limpiar playlist
                original_count = len(playlist)
                cleaned_playlist = clean_playlist(playlist)
                cleaned_count = len(cleaned_playlist)

                # Verificar coherencia
                is_coherent = web_songs_count == cleaned_count

                if is_coherent:
                    results["coherent_episodes"] += 1
                else:
                    results["incoherent_episodes"] += 1

                    # Si se eliminaron canciones, actualizar la base de datos
                    if cleaned_count < original_count:
                        print(f"\n🔧 Actualizando episodio #{program_number}...")
                        print(
                            f"   Antes: {original_count} canciones, web_songs_count: {web_songs_count}"
                        )
                        print(f"   Después: {cleaned_count} canciones")

                        try:
                            db.update_web_info(
                                podcast_id=episode_id,
                                web_playlist=json.dumps(
                                    cleaned_playlist, ensure_ascii=False
                                ),
                                web_songs_count=cleaned_count,
                            )
                            results["cleaned_episodes"] += 1
                            print("   ✅ Actualizado correctamente")
                        except Exception as e:
                            error_msg = (
                                f"Error actualizando episodio #{program_number}: {e}"
                            )
                            results["errors"].append(
                                {
                                    "program_number": program_number,
                                    "title": title,
                                    "error": error_msg,
                                }
                            )
                            print(f"   ❌ {error_msg}")

                # Guardar detalles
                results["details"].append(
                    {
                        "program_number": program_number,
                        "title": title,
                        "original_count": original_count,
                        "cleaned_count": cleaned_count,
                        "web_songs_count": web_songs_count,
                        "is_coherent": is_coherent,
                        "was_cleaned": cleaned_count < original_count,
                    }
                )

            except json.JSONDecodeError as e:
                error_msg = f"Error parseando JSON: {e}"
                results["errors"].append(
                    {
                        "program_number": program_number,
                        "title": title,
                        "error": error_msg,
                    }
                )
            except Exception as e:
                error_msg = f"Error procesando episodio: {e}"
                results["errors"].append(
                    {
                        "program_number": program_number,
                        "title": title,
                        "error": error_msg,
                    }
                )

        return results

    except Exception as e:
        print(f"❌ Error obteniendo episodios: {e}")
        return {"error": str(e)}


def generate_report(results: dict[str, Any]) -> str:
    """
    Genera un reporte en markdown de los resultados.
    """
    if "error" in results:
        return f"# ❌ Error en la verificación\n\n{results['error']}"

    report = f"""# 🧹 Limpieza de Enlaces en web_playlist

## 📊 Resumen

- **Total de episodios analizados**: {results['total_episodes']}
- **Episodios coherentes**: {results['coherent_episodes']} ({results['coherent_episodes']/results['total_episodes']*100:.1f}%)
- **Episodios incoherentes**: {results['incoherent_episodes']} ({results['incoherent_episodes']/results['total_episodes']*100:.1f}%)
- **Episodios limpiados**: {results['cleaned_episodes']}
- **Errores**: {len(results['errors'])}

## 🔧 Episodios Limpiados

"""

    if results["cleaned_episodes"] > 0:
        cleaned_details = [d for d in results["details"] if d["was_cleaned"]]
        for detail in cleaned_details:
            report += f"- **#{detail['program_number']}** - {detail['title']}\n"
            report += f"  - Antes: {detail['original_count']} canciones\n"
            report += f"  - Después: {detail['cleaned_count']} canciones\n"
            report += f"  - web_songs_count: {detail['web_songs_count']} → {detail['cleaned_count']}\n\n"
    else:
        report += "No se encontraron episodios que necesitaran limpieza.\n\n"

    # Episodios incoherentes que no se pudieron limpiar
    incoherent_details = [
        d for d in results["details"] if not d["is_coherent"] and not d["was_cleaned"]
    ]
    if incoherent_details:
        report += "## ⚠️ Episodios Incoherentes (No Limpiados)\n\n"
        for detail in incoherent_details:
            report += f"- **#{detail['program_number']}** - {detail['title']}\n"
            report += f"  - Canciones en playlist: {detail['cleaned_count']}\n"
            report += f"  - web_songs_count: {detail['web_songs_count']}\n\n"

    # Errores
    if results["errors"]:
        report += "## ❌ Errores\n\n"
        for error in results["errors"]:
            report += f"- **#{error['program_number']}** - {error['title']}\n"
            report += f"  - Error: {error['error']}\n\n"

    return report


def main():
    """
    Función principal del script.
    """
    print("🧹 Limpiador de Enlaces en web_playlist")
    print("=" * 50)

    try:
        # Conectar a Supabase
        db = SupabaseDatabase()
        print("✅ Conexión a Supabase establecida")

        # Verificar coherencia y limpiar
        results = verify_web_songs_count_coherence(db)

        # Generar reporte
        report = generate_report(results)

        # Mostrar resumen
        print("\n" + "=" * 50)
        print("📋 RESUMEN")
        print("=" * 50)

        if "error" in results:
            print(f"❌ Error: {results['error']}")
        else:
            print(f"📊 Total de episodios analizados: {results['total_episodes']}")
            print(f"✅ Episodios coherentes: {results['coherent_episodes']}")
            print(f"⚠️  Episodios incoherentes: {results['incoherent_episodes']}")
            print(f"🔧 Episodios limpiados: {results['cleaned_episodes']}")
            print(f"❌ Errores: {len(results['errors'])}")

        # Guardar reporte
        report_filename = f"reports/limpieza_web_playlist_{results.get('total_episodes', 0)}_episodios.md"
        with open(report_filename, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"\n📄 Reporte guardado en: {report_filename}")

        # Mostrar reporte completo
        print("\n" + "=" * 50)
        print("📄 REPORTE COMPLETO")
        print("=" * 50)
        print(report)

    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
