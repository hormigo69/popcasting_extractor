import os
import sys
from pathlib import Path
from urllib.parse import urlparse

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))


from dotenv import load_dotenv
from supabase_database import get_supabase_connection

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "services"))


#!/usr/bin/env python3
"""
Script para analizar las URLs de WordPress y ver qué tipos tenemos.
"""


# Cargar variables de entorno
load_dotenv()

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(str(Path(__file__).parent.parent.parent))


def get_episodes_with_wordpress_urls():
    """
    Obtiene episodios que tienen wordpress_url.
    """
    try:
        db = get_supabase_connection()
        response = (
            db.client.table("podcasts")
            .select(
                "id, program_number, title, date, web_playlist, web_songs_count, wordpress_url"
            )
            .not_.is_("wordpress_url", "null")
            .order("program_number")
            .execute()
        )

        return response.data
    except Exception as e:
        print(f"❌ Error obteniendo episodios: {e}")
        return []


def analyze_urls():
    """
    Analiza las URLs de WordPress.
    """
    print("🔍 Analizador de URLs de WordPress")
    print("=" * 40)

    episodes = get_episodes_with_wordpress_urls()

    if not episodes:
        print("✅ No hay episodios con wordpress_url.")
        return

    print(f"📊 Encontrados {len(episodes)} episodios con wordpress_url")
    print()

    # Categorizar URLs
    url_types = {}
    low_songs_episodes = []

    for episode in episodes:
        url = episode["wordpress_url"]
        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        if domain not in url_types:
            url_types[domain] = []
        url_types[domain].append(episode)

        # Episodios con pocas canciones
        if episode["web_songs_count"] <= 8:
            low_songs_episodes.append(episode)

    print("📋 Tipos de URLs encontradas:")
    for domain, episodes_list in url_types.items():
        print(f"   {domain}: {len(episodes_list)} episodios")

    print()
    print(f"🎵 Episodios con 8 canciones o menos: {len(low_songs_episodes)}")
    print()

    if low_songs_episodes:
        print("📝 Episodios con pocas canciones:")
        for episode in low_songs_episodes[:10]:  # Mostrar solo los primeros 10
            print(
                f"   #{episode['program_number']}: {episode['web_songs_count']} canciones | {episode['wordpress_url']}"
            )

        if len(low_songs_episodes) > 10:
            print(f"   ... y {len(low_songs_episodes) - 10} más")


def main():
    """
    Función principal.
    """
    analyze_urls()


if __name__ == "__main__":
    main()
