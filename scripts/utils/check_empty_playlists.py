#!/usr/bin/env python3
"""
Script para verificar cuántos episodios tienen playlists vacías y cuáles son.
"""

import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from services.supabase_database import SupabaseDatabase


def check_empty_playlists(db: SupabaseDatabase):
    """
    Verifica qué episodios tienen playlists vacías.
    """
    print("🔍 Verificando episodios con playlists vacías...")

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

        empty_playlists = []
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

                # Verificar si está vacío
                if not isinstance(playlist, list) or len(playlist) == 0:
                    empty_playlists.append(
                        {
                            "program_number": program_number,
                            "title": title,
                            "web_songs_count": web_songs_count,
                            "playlist_type": "no es lista"
                            if not isinstance(playlist, list)
                            else "lista vacía",
                            "raw_playlist": web_playlist[:200] + "..."
                            if len(web_playlist) > 200
                            else web_playlist,
                        }
                    )

            except json.JSONDecodeError:
                empty_playlists.append(
                    {
                        "program_number": program_number,
                        "title": title,
                        "web_songs_count": web_songs_count,
                        "playlist_type": "JSON inválido",
                        "raw_playlist": web_playlist[:200] + "..."
                        if len(web_playlist) > 200
                        else web_playlist,
                    }
                )
            except Exception as e:
                print(f"Error procesando episodio #{program_number}: {e}")
                continue

        return empty_playlists, total_episodes

    except Exception as e:
        print(f"❌ Error obteniendo episodios: {e}")
        return [], 0


def generate_report(empty_playlists, total_episodes):
    """
    Genera un reporte de los episodios con playlists vacías.
    """
    report = f"""# 🔍 Verificación de Playlists Vacías en web_playlist

## 📊 Resumen

- **Total de episodios analizados**: {total_episodes}
- **Episodios con playlists vacías**: {len(empty_playlists)}
- **Porcentaje problemático**: {len(empty_playlists)/total_episodes*100:.1f}%

"""

    if empty_playlists:
        report += "## ⚠️ Episodios con Playlists Vacías\n\n"

        # Ordenar por número de programa
        empty_playlists.sort(key=lambda x: x["program_number"])

        for episode in empty_playlists:
            report += f"### #{episode['program_number']} - {episode['title']}\n\n"
            report += f"- **Tipo de problema**: {episode['playlist_type']}\n"
            report += f"- **web_songs_count**: {episode['web_songs_count']}\n"
            report += f"- **Contenido raw**: `{episode['raw_playlist']}`\n\n"
    else:
        report += "## ✅ No Hay Playlists Vacías\n\n"
        report += "¡Excelente! Todos los episodios tienen playlists válidas.\n\n"

    return report


def main():
    """
    Función principal del script.
    """
    print("🔍 Verificador de Playlists Vacías en web_playlist")
    print("=" * 60)

    try:
        # Conectar a Supabase
        db = SupabaseDatabase()
        print("✅ Conexión a Supabase establecida")

        # Verificar playlists vacías
        empty_playlists, total_episodes = check_empty_playlists(db)

        # Generar reporte
        report = generate_report(empty_playlists, total_episodes)

        # Mostrar resumen
        print("\n" + "=" * 60)
        print("📋 RESUMEN")
        print("=" * 60)

        print(f"📊 Total de episodios analizados: {total_episodes}")
        print(f"⚠️  Episodios con playlists vacías: {len(empty_playlists)}")
        print(
            f"📈 Porcentaje problemático: {len(empty_playlists)/total_episodes*100:.1f}%"
        )

        if empty_playlists:
            print("\n🔢 Números de programa con playlists vacías:")
            program_numbers = [ep["program_number"] for ep in empty_playlists]
            program_numbers.sort()
            print(f"   {', '.join(map(str, program_numbers))}")

            print("\n📝 Tipos de problemas encontrados:")
            problem_types = {}
            for ep in empty_playlists:
                problem_type = ep["playlist_type"]
                if problem_type not in problem_types:
                    problem_types[problem_type] = 0
                problem_types[problem_type] += 1

            for problem_type, count in problem_types.items():
                print(f"   - {problem_type}: {count} episodios")

        # Guardar reporte
        report_filename = (
            f"reports/verificacion_playlists_vacias_{total_episodes}_episodios.md"
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
