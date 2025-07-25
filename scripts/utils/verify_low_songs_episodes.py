#!/usr/bin/env python3
"""
import json
import sys
from pathlib import Path
from dotenv import load_dotenv
from config import DATABASE_TYPE
from database import get_db_connection, initialize_database
from supabase_database import get_supabase_connection

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services"))

Script para revisar episodios con menos de 9 canciones y verificar si tienen playlists completas.
"""

# Cargar variables de entorno
load_dotenv()

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent.parent))


def get_database_wrapper():
    """
    Obtiene la instancia de base de datos correcta según la configuración.
    """
    if DATABASE_TYPE == "supabase":
        return get_supabase_connection()
    else:
        initialize_database()

        # Crear un wrapper para mantener compatibilidad con la interfaz
        class DatabaseWrapper:
            def __init__(self, conn):
                self.conn = conn
                self.cursor = conn.cursor()

            def get_episodes_with_few_songs(self, max_songs=8):
                self.cursor.execute(
                    """
                    SELECT id, program_number, title, date, web_playlist, web_songs_count, wordpress_url
                    FROM podcasts
                    WHERE web_songs_count IS NOT NULL AND web_songs_count <= ?
                    ORDER BY web_songs_count, program_number
                """,
                    (max_songs,),
                )
                return [dict(row) for row in self.cursor.fetchall()]

        return DatabaseWrapper(get_db_connection())


def analyze_low_songs_episodes():
    """
    Analiza episodios con pocas canciones para detectar posibles errores.
    """
    try:
        db = get_database_wrapper()
        print("✅ Conexión a la base de datos establecida")

        # Obtener episodios con 8 canciones o menos
        if DATABASE_TYPE == "supabase":
            response = (
                db.client.table("podcasts")
                .select(
                    "id, program_number, title, date, web_playlist, web_songs_count, wordpress_url"
                )
                .not_.is_("web_songs_count", "null")
                .lte("web_songs_count", 8)
                .order("web_songs_count", desc=True)
                .execute()
            )

            episodes = response.data
        else:
            episodes = db.get_episodes_with_few_songs(8)

        print("\n🔍 REVISIÓN DE EPISODIOS CON 8 CANCIONES O MENOS")
        print("=" * 60)
        print(f"Total de episodios a revisar: {len(episodes)}")

        if not episodes:
            print("✅ No hay episodios con 8 canciones o menos.")
            return

        # Agrupar por número de canciones
        by_count = {}
        for ep in episodes:
            count = ep["web_songs_count"]
            if count not in by_count:
                by_count[count] = []
            by_count[count].append(ep)

        # Analizar cada grupo
        for songs_count in sorted(by_count.keys(), reverse=True):
            episodes_group = by_count[songs_count]
            print(
                f"\n📊 EPISODIOS CON {songs_count} CANCIÓN{'ES' if songs_count > 1 else ''}"
            )
            print("-" * 50)

            for ep in episodes_group:
                print(
                    f"\n🎵 #{ep['program_number']} | {ep['date']} | {ep['title'][:50]}..."
                )

                # Verificar si tiene playlist
                playlist_json = ep.get("web_playlist")
                if playlist_json:
                    try:
                        playlist = json.loads(playlist_json)
                        print(f"   ✅ Tiene playlist con {len(playlist)} canciones:")

                        # Mostrar las canciones
                        for i, song in enumerate(
                            playlist[:5]
                        ):  # Mostrar solo las primeras 5
                            print(
                                f"      {i+1}. {song.get('artist', 'N/A')} - {song.get('title', 'N/A')}"
                            )

                        if len(playlist) > 5:
                            print(f"      ... y {len(playlist) - 5} más")

                        # Verificar si parece una playlist completa
                        if len(playlist) < 9:
                            print(
                                f"   ⚠️  PLAYLIST CORTA - Solo {len(playlist)} canciones"
                            )
                            if ep.get("wordpress_url"):
                                print(f"   🔗 URL: {ep['wordpress_url']}")

                    except json.JSONDecodeError:
                        print("   ❌ Error parseando playlist JSON")
                else:
                    print("   ❌ No tiene playlist")
                    if ep.get("wordpress_url"):
                        print(f"   🔗 URL: {ep['wordpress_url']}")

        # Resumen de posibles problemas
        print("\n📋 RESUMEN DE POSIBLES PROBLEMAS")
        print("=" * 40)

        problematic_episodes = []
        for ep in episodes:
            playlist_json = ep.get("web_playlist")
            if playlist_json:
                try:
                    playlist = json.loads(playlist_json)
                    if len(playlist) < 9:
                        problematic_episodes.append(
                            {
                                "program_number": ep["program_number"],
                                "songs_count": len(playlist),
                                "title": ep["title"],
                                "url": ep.get("wordpress_url"),
                            }
                        )
                except Exception:
                    pass

        if problematic_episodes:
            print(
                f"⚠️  Se encontraron {len(problematic_episodes)} episodios con playlists sospechosamente cortas:"
            )
            for ep in problematic_episodes:
                print(
                    f"   #{ep['program_number']} | {ep['songs_count']} canciones | {ep['title'][:40]}..."
                )
                if ep["url"]:
                    print(f"      URL: {ep['url']}")
        else:
            print("✅ No se detectaron problemas evidentes.")

        return episodes

    except Exception as e:
        print(f"❌ Error: {e}")
        return []


def main():
    """Función principal del script."""
    print("🔍 Verificador de episodios con pocas canciones")
    print("=" * 50)

    episodes = analyze_low_songs_episodes()

    print("\n✅ Revisión completada")
    if episodes:
        print(f"📊 Se revisaron {len(episodes)} episodios con 8 canciones o menos")


if __name__ == "__main__":
    main()
