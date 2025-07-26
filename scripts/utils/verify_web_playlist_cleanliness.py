#!/usr/bin/env python3
"""
Script para verificar que las playlists estén completamente limpias de enlaces
y generar un reporte detallado de la limpieza realizada.
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
        r"blip\.tv",  # Dominio blip.tv
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


def analyze_playlist(playlist: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Analiza una playlist para detectar problemas.
    """
    if not playlist or not isinstance(playlist, list):
        return {
            "total_songs": 0,
            "valid_songs": 0,
            "url_songs": 0,
            "empty_title_songs": 0,
            "short_title_songs": 0,
            "suspicious_songs": 0,
            "problems": [],
        }

    analysis = {
        "total_songs": len(playlist),
        "valid_songs": 0,
        "url_songs": 0,
        "empty_title_songs": 0,
        "short_title_songs": 0,
        "suspicious_songs": 0,
        "problems": [],
    }

    for i, song in enumerate(playlist):
        if not isinstance(song, dict):
            analysis["problems"].append(f"Canción {i+1}: No es un diccionario válido")
            continue

        artist = song.get("artist", "")
        title = song.get("title", "")

        # Verificar si el artista o título son URLs
        if is_url(artist) or is_url(title):
            analysis["url_songs"] += 1
            analysis["problems"].append(
                f"Canción {i+1}: Contiene URL - Artista: '{artist}', Título: '{title}'"
            )
            continue

        # Verificar si el título está vacío
        if not title or title.strip() == "":
            analysis["empty_title_songs"] += 1
            analysis["problems"].append(
                f"Canción {i+1}: Título vacío - Artista: '{artist}'"
            )
            continue

        # Verificar si el título es muy corto
        if len(title.strip()) < 2:
            analysis["short_title_songs"] += 1
            analysis["problems"].append(
                f"Canción {i+1}: Título muy corto - Artista: '{artist}', Título: '{title}'"
            )
            continue

        # Verificar si contiene palabras clave sospechosas
        if any(
            keyword in title.lower()
            for keyword in ["http", "www", ".com", ".mp3", "ivoox", "blip.tv"]
        ):
            analysis["suspicious_songs"] += 1
            analysis["problems"].append(
                f"Canción {i+1}: Palabras clave sospechosas - Artista: '{artist}', Título: '{title}'"
            )
            continue

        analysis["valid_songs"] += 1

    return analysis


def verify_all_playlists(db: SupabaseDatabase) -> dict[str, Any]:
    """
    Verifica todas las playlists en la base de datos.
    """
    print("🔍 Verificando limpieza de todas las playlists...")

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
            "clean_episodes": 0,
            "problematic_episodes": 0,
            "total_songs": 0,
            "valid_songs": 0,
            "url_songs": 0,
            "empty_title_songs": 0,
            "short_title_songs": 0,
            "suspicious_songs": 0,
            "errors": [],
            "problematic_details": [],
        }

        for episode in episodes:
            episode["id"]
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

                # Analizar playlist
                analysis = analyze_playlist(playlist)

                # Actualizar estadísticas globales
                results["total_songs"] += analysis["total_songs"]
                results["valid_songs"] += analysis["valid_songs"]
                results["url_songs"] += analysis["url_songs"]
                results["empty_title_songs"] += analysis["empty_title_songs"]
                results["short_title_songs"] += analysis["short_title_songs"]
                results["suspicious_songs"] += analysis["suspicious_songs"]

                # Verificar si el episodio tiene problemas
                has_problems = (
                    analysis["url_songs"] > 0
                    or analysis["empty_title_songs"] > 0
                    or analysis["short_title_songs"] > 0
                    or analysis["suspicious_songs"] > 0
                )

                if has_problems:
                    results["problematic_episodes"] += 1
                    results["problematic_details"].append(
                        {
                            "program_number": program_number,
                            "title": title,
                            "web_songs_count": web_songs_count,
                            "analysis": analysis,
                        }
                    )
                else:
                    results["clean_episodes"] += 1

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


def generate_verification_report(results: dict[str, Any]) -> str:
    """
    Genera un reporte detallado de la verificación.
    """
    if "error" in results:
        return f"# ❌ Error en la verificación\n\n{results['error']}"

    report = f"""# 🔍 Verificación de Limpieza de web_playlist

## 📊 Resumen General

- **Total de episodios analizados**: {results['total_episodes']}
- **Episodios limpios**: {results['clean_episodes']} ({results['clean_episodes']/results['total_episodes']*100:.1f}%)
- **Episodios problemáticos**: {results['problematic_episodes']} ({results['problematic_episodes']/results['total_episodes']*100:.1f}%)
- **Errores**: {len(results['errors'])}

## 🎵 Estadísticas de Canciones

- **Total de canciones**: {results['total_songs']}
- **Canciones válidas**: {results['valid_songs']} ({results['valid_songs']/results['total_songs']*100:.1f}%)
- **Canciones con URLs**: {results['url_songs']} ({results['url_songs']/results['total_songs']*100:.1f}%)
- **Canciones con título vacío**: {results['empty_title_songs']} ({results['empty_title_songs']/results['total_songs']*100:.1f}%)
- **Canciones con título corto**: {results['short_title_songs']} ({results['short_title_songs']/results['total_songs']*100:.1f}%)
- **Canciones sospechosas**: {results['suspicious_songs']} ({results['suspicious_songs']/results['total_songs']*100:.1f}%)

"""

    if results["problematic_episodes"] > 0:
        report += "## ⚠️ Episodios Problemáticos\n\n"

        for detail in results["problematic_details"]:
            analysis = detail["analysis"]
            report += f"### #{detail['program_number']} - {detail['title']}\n\n"
            report += f"- **web_songs_count**: {detail['web_songs_count']}\n"
            report += f"- **Total canciones**: {analysis['total_songs']}\n"
            report += f"- **Canciones válidas**: {analysis['valid_songs']}\n"
            report += f"- **Canciones con URLs**: {analysis['url_songs']}\n"
            report += (
                f"- **Canciones con título vacío**: {analysis['empty_title_songs']}\n"
            )
            report += (
                f"- **Canciones con título corto**: {analysis['short_title_songs']}\n"
            )
            report += f"- **Canciones sospechosas**: {analysis['suspicious_songs']}\n\n"

            if analysis["problems"]:
                report += "**Problemas detectados:**\n"
                for problem in analysis["problems"]:
                    report += f"- {problem}\n"
                report += "\n"
    else:
        report += "## ✅ Todos los Episodios Están Limpios\n\n"
        report += "¡Excelente! No se encontraron episodios problemáticos.\n\n"

    # Errores
    if results["errors"]:
        report += "## ❌ Errores\n\n"
        for error in results["errors"]:
            report += f"- **#{error['program_number']}** - {error['title']}\n"
            report += f"  - Error: {error['error']}\n\n"

    # Recomendaciones
    report += "## 💡 Recomendaciones\n\n"

    if results["url_songs"] > 0:
        report += "- ⚠️ **Hay canciones con URLs**: Ejecutar nuevamente el script de limpieza\n"

    if results["empty_title_songs"] > 0:
        report += "- ⚠️ **Hay canciones con títulos vacíos**: Revisar manualmente estos episodios\n"

    if results["suspicious_songs"] > 0:
        report += (
            "- ⚠️ **Hay canciones sospechosas**: Verificar manualmente estas canciones\n"
        )

    if results["clean_episodes"] == results["total_episodes"]:
        report += "- ✅ **Todas las playlists están limpias**: No se requieren acciones adicionales\n"

    return report


def main():
    """
    Función principal del script.
    """
    print("🔍 Verificador de Limpieza de web_playlist")
    print("=" * 50)

    try:
        # Conectar a Supabase
        db = SupabaseDatabase()
        print("✅ Conexión a Supabase establecida")

        # Verificar todas las playlists
        results = verify_all_playlists(db)

        # Generar reporte
        report = generate_verification_report(results)

        # Mostrar resumen
        print("\n" + "=" * 50)
        print("📋 RESUMEN")
        print("=" * 50)

        if "error" in results:
            print(f"❌ Error: {results['error']}")
        else:
            print(f"📊 Total de episodios analizados: {results['total_episodes']}")
            print(f"✅ Episodios limpios: {results['clean_episodes']}")
            print(f"⚠️  Episodios problemáticos: {results['problematic_episodes']}")
            print(f"🎵 Total de canciones: {results['total_songs']}")
            print(f"✅ Canciones válidas: {results['valid_songs']}")
            print(f"🔗 Canciones con URLs: {results['url_songs']}")
            print(f"❌ Errores: {len(results['errors'])}")

        # Guardar reporte
        report_filename = f"reports/verificacion_limpieza_web_playlist_{results.get('total_episodes', 0)}_episodios.md"
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
