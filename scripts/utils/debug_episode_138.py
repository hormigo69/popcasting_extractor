#!/usr/bin/env python3
"""
Script para diagnosticar el problema del episodio 138.
Verifica por qué no se está parseando correctamente la playlist.
"""

import sys
from pathlib import Path

# Agregar el directorio del sincronizador al path
sincronizador_path = Path(__file__).parent.parent.parent / "sincronizador_rss" / "src"
sys.path.insert(0, str(sincronizador_path))

# Imports después de modificar el path
from components.config_manager import ConfigManager  # noqa: E402
from components.wordpress_client import WordPressClient  # noqa: E402


def debug_episode_138():
    """
    Diagnostica el problema del episodio 138.
    """
    print("🔍 Diagnóstico del Episodio 138")
    print("=" * 60)

    try:
        # Inicializar componentes
        config_manager = ConfigManager()
        wordpress_config = config_manager.get_wordpress_config()
        wordpress_client = WordPressClient(wordpress_config["api_url"])

        print("✅ Componentes inicializados")

        # Obtener datos del episodio 138
        print("\n📻 Obteniendo datos del episodio 138...")
        episode_data = wordpress_client.get_post_details_by_date_and_number(
            "2011-03-01", "138"
        )

        if not episode_data:
            print("❌ No se pudieron obtener datos del episodio 138")
            return

        print("✅ Datos obtenidos del episodio 138")

        # Mostrar datos crudos
        print("\n📄 DATOS CRUDOS:")
        print(f"Título: {episode_data.get('title', 'N/A')}")
        print(f"URL: {episode_data.get('wordpress_url', 'N/A')}")
        print(f"Imagen: {episode_data.get('cover_image_url', 'N/A')}")
        print(f"Enlaces extra: {len(episode_data.get('web_extra_links', []))}")

        # Analizar la playlist
        playlist = episode_data.get("web_playlist", [])
        print("\n🎵 PLAYLIST CRUDA:")
        print(f"Número de canciones: {len(playlist)}")

        for i, song in enumerate(playlist, 1):
            print(f"\nCanción {i}:")
            print(f"  Position: {song.get('position', 'N/A')}")
            print(f"  Artist: {song.get('artist', 'N/A')}")
            print(f"  Title: {song.get('title', 'N/A')}")

        # Probar el parsing manual
        print("\n🔧 PRUEBA DE PARSING MANUAL:")
        if playlist and len(playlist) > 0:
            first_song = playlist[0]
            title_text = first_song.get("title", "")

            print(f"Texto a parsear: {title_text}")

            # Probar el método de parsing
            songs = wordpress_client._parse_popcasting_playlist_text(title_text)
            print(f"\nResultado del parsing: {len(songs)} canciones encontradas")

            for i, song in enumerate(songs, 1):
                print(
                    f"  {i}. {song.get('artist', 'N/A')} - {song.get('title', 'N/A')}"
                )

        # Probar con el texto original del párrafo
        print("\n🔧 PRUEBA CON TEXTO ORIGINAL:")
        # Simular el texto que se extrajo originalmente
        original_text = "bob dylan ┬Ę suze (the cough song)┬Ā - :┬Ā pete drake ┬Ę the spook┬Ā ::┬Ā the cookies ┬Ę i never dreamed┬Ā ::┬Ā the sinceres ┬Ę if you should leave me┬Ā ::┬Ā the sand band ┬Ę set me free┬Ā ::┬Ā fleetwood mac ┬Ę dreams┬Ā ::┬Ā virgo ┬Ę my space┬Ā ::┬Ā tim buckley ┬Ę aren't you the girl (demo)┬Ā ::┬Ā chuck berry ┬Ę blues for hawaiians┬Ā ::┬Ā pj harvey ┬Ę the guns called me back again┬Ā ::┬Ā warpaint ┬Ę ashes to ashes┬Ā ::┬Ā sister crayon ┬Ę the bewley brothers┬Ā ::┬Ā florrie ┬Ę left too late"

        print(f"Texto original: {original_text}")

        # Limpiar el texto
        cleaned_text = wordpress_client._clean_unicode_text(original_text)
        print(f"Texto limpiado: {cleaned_text}")

        # Probar parsing
        songs = wordpress_client._parse_popcasting_playlist_text(cleaned_text)
        print(f"\nResultado del parsing: {len(songs)} canciones encontradas")

        for i, song in enumerate(songs, 1):
            print(f"  {i}. {song.get('artist', 'N/A')} - {song.get('title', 'N/A')}")

        # Probar parsing individual
        print("\n🔧 PRUEBA DE PARSING INDIVIDUAL:")
        parts = cleaned_text.split("::")
        print(f"Partes separadas por '::': {len(parts)}")

        for i, part in enumerate(parts, 1):
            part = part.strip()
            print(f"\nParte {i}: '{part}'")

            song_info = wordpress_client._parse_song_text(part)
            if song_info:
                print(
                    f"  ✅ Parseado: {song_info.get('artist', 'N/A')} - {song_info.get('title', 'N/A')}"
                )
            else:
                print("  ❌ No se pudo parsear")

    except Exception as e:
        print(f"❌ Error durante el diagnóstico: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    debug_episode_138()
