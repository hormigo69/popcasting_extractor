#!/usr/bin/env python3
"""
Script para verificar qué episodios no empiezan con position 1 en su web_playlist.
"""

import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.supabase_database import SupabaseDatabase


def check_playlist_starting_positions(db: SupabaseDatabase):
    """
    Verifica qué episodios no empiezan con position 1 en su web_playlist.
    """
    print("🔍 Verificando episodios que no empiezan con position 1...")

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

        problematic_episodes = []
        total_episodes = len(episodes)

        for episode in episodes:
            episode["id"]
            program_number = episode["program_number"]
            title = episode["title"]
            web_playlist = episode["web_playlist"]
            web_songs_count = episode["web_songs_count"]

            try:
                # Parsear web_playlist
                playlist = json.loads(web_playlist)
                if not isinstance(playlist, list) or len(playlist) == 0:
                    continue

                # Verificar la primera canción
                first_song = playlist[0]
                if not isinstance(first_song, dict):
                    continue

                first_position = first_song.get("position")

                if first_position != 1:
                    problematic_episodes.append(
                        {
                            "program_number": program_number,
                            "title": title,
                            "web_songs_count": web_songs_count,
                            "first_position": first_position,
                            "total_songs": len(playlist),
                            "first_song": first_song,
                        }
                    )

            except json.JSONDecodeError:
                continue
            except Exception as e:
                print(f"Error procesando episodio #{program_number}: {e}")
                continue

        return problematic_episodes, total_episodes

    except Exception as e:
        print(f"❌ Error obteniendo episodios: {e}")
        return [], 0


def generate_report(problematic_episodes, total_episodes):
    """
    Genera un reporte de los episodios problemáticos.
    """
    report = f"""# 🔍 Verificación de Posiciones de Inicio en web_playlist

## 📊 Resumen

- **Total de episodios analizados**: {total_episodes}
- **Episodios que NO empiezan con position 1**: {len(problematic_episodes)}
- **Porcentaje problemático**: {len(problematic_episodes)/total_episodes*100:.1f}%

"""

    if problematic_episodes:
        report += "## ⚠️ Episodios que NO empiezan con position 1\n\n"

        # Ordenar por número de programa
        problematic_episodes.sort(key=lambda x: x["program_number"])

        for episode in problematic_episodes:
            report += f"### #{episode['program_number']} - {episode['title']}\n\n"
            report += f"- **Primera posición**: {episode['first_position']}\n"
            report += f"- **Total de canciones**: {episode['total_songs']}\n"
            report += f"- **web_songs_count**: {episode['web_songs_count']}\n"

            first_song = episode["first_song"]
            artist = first_song.get("artist", "N/A")
            title = first_song.get("title", "N/A")
            report += f"- **Primera canción**: {artist} - {title}\n\n"
    else:
        report += "## ✅ Todos los Episodios Empiezan Correctamente\n\n"
        report += "¡Excelente! Todos los episodios empiezan con position 1.\n\n"

    return report


def main():
    """
    Función principal del script.
    """
    print("🔍 Verificador de Posiciones de Inicio en web_playlist")
    print("=" * 60)

    try:
        # Conectar a Supabase
        db = SupabaseDatabase()
        print("✅ Conexión a Supabase establecida")

        # Verificar posiciones de inicio
        problematic_episodes, total_episodes = check_playlist_starting_positions(db)

        # Generar reporte
        report = generate_report(problematic_episodes, total_episodes)

        # Mostrar resumen
        print("\n" + "=" * 60)
        print("📋 RESUMEN")
        print("=" * 60)

        print(f"📊 Total de episodios analizados: {total_episodes}")
        print(
            f"⚠️  Episodios que NO empiezan con position 1: {len(problematic_episodes)}"
        )
        print(
            f"📈 Porcentaje problemático: {len(problematic_episodes)/total_episodes*100:.1f}%"
        )

        if problematic_episodes:
            print("\n🔢 Números de programa problemáticos:")
            program_numbers = [ep["program_number"] for ep in problematic_episodes]
            program_numbers.sort()
            print(f"   {', '.join(map(str, program_numbers))}")

        # Guardar reporte
        report_filename = (
            f"reports/verificacion_posiciones_inicio_{total_episodes}_episodios.md"
        )
        with open(report_filename, "w", encoding="utf-8") as f:
            f.write(report)

        print(f"\n📄 Reporte guardado en: {report_filename}")

        # Mostrar reporte completo
        print("\n" + "=" * 60)
        print("📄 REPORTE COMPLETO")
        print("=" * 60)
        print(report)

    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
