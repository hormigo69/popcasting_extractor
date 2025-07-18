#!/usr/bin/env python3
"""
Script de prueba para verificar la nueva funcionalidad de extracción de links mejorada
"""

import feedparser

from services import database as db
from services.popcasting_extractor import PopcastingExtractor


def test_enhanced_link_extraction():
    """Prueba la extracción mejorada de links"""
    print("🔍 Probando extracción mejorada de links de episodios")

    # Crear instancia del extractor
    extractor = PopcastingExtractor()

    # Probar con el feed RSS
    feed_url = "https://feeds.feedburner.com/Popcasting"

    try:
        print(f"📡 Obteniendo feed de: {feed_url}")
        feed = feedparser.parse(feed_url)

        if not feed.entries:
            print("❌ No se encontraron episodios")
            return

        print(f"✅ Encontrados {len(feed.entries)} episodios")

        # Probar con los primeros 3 episodios
        for i, entry in enumerate(feed.entries[:3]):
            print(f"\n--- Probando Episodio {i+1} ---")
            print(f"Título: {entry.get('title', 'Sin título')}")

            # Extraer datos usando nuestro método mejorado
            episode_data = extractor._extract_episode_data(entry)

            if episode_data:
                print("✅ Datos extraídos correctamente:")
                print(f"  • Número de programa: {episode_data['program_number']}")
                print(f"  • Fecha: {episode_data['published_date']}")
                print(f"  • URL web: {episode_data['ivoox_web_url']}")
                print(f"  • URL descarga: {episode_data['ivoox_download_url']}")
                print(f"  • Tamaño archivo: {episode_data['file_size']} bytes")
                if episode_data["file_size"]:
                    size_mb = episode_data["file_size"] / (1024 * 1024)
                    print(f"  • Tamaño archivo: {size_mb:.1f} MB")
                print(f"  • Canciones encontradas: {len(episode_data['playlist'])}")
            else:
                print("❌ Error al extraer datos del episodio")

    except Exception as e:
        print(f"❌ Error al procesar el feed: {e}")


def test_database_integration():
    """Prueba la integración con la base de datos"""
    print(f"\n{'='*60}")
    print("Probando integración con la base de datos")
    print(f"{'='*60}")

    try:
        # Inicializar base de datos
        print("🗄️  Inicializando base de datos...")
        db.initialize_database()

        # Probar añadir un podcast con links
        print("📝 Probando añadir podcast con links...")
        podcast_id = db.add_podcast_if_not_exists(
            title="Test Episode with Links",
            date="2024-01-15",
            url="https://www.ivoox.com/test-episode.html",
            program_number="TEST001",
            download_url="https://www.ivoox.com/test-episode.mp3",
            file_size=104857600,  # 100MB
        )

        print(f"✅ Podcast añadido con ID: {podcast_id}")

        # Verificar que se guardó correctamente
        podcasts = db.get_all_podcasts()
        test_podcast = None
        for podcast in podcasts:
            if podcast["title"] == "Test Episode with Links":
                test_podcast = podcast
                break

        if test_podcast:
            print("✅ Podcast encontrado en la base de datos:")
            print(f"  • ID: {test_podcast['id']}")
            print(f"  • Título: {test_podcast['title']}")
            print(f"  • URL: {test_podcast['url']}")
            print(f"  • Download URL: {test_podcast['download_url']}")
            print(f"  • File Size: {test_podcast['file_size']} bytes")
            if test_podcast["file_size"]:
                size_mb = test_podcast["file_size"] / (1024 * 1024)
                print(f"  • File Size: {size_mb:.1f} MB")
        else:
            print("❌ No se encontró el podcast de prueba")

    except Exception as e:
        print(f"❌ Error en la integración con la base de datos: {e}")


def test_full_extraction():
    """Prueba la extracción completa con la nueva funcionalidad"""
    print(f"\n{'='*60}")
    print("Probando extracción completa con nueva funcionalidad")
    print(f"{'='*60}")

    try:
        # Crear instancia del extractor
        extractor = PopcastingExtractor()

        # Ejecutar extracción completa
        print("🚀 Ejecutando extracción completa...")
        extractor.run()

        # Verificar resultados
        podcasts = db.get_all_podcasts()
        print("\n📊 Resultados de la extracción:")
        print(f"  • Total de podcasts en BD: {len(podcasts)}")

        # Mostrar los últimos 5 podcasts con información de links
        recent_podcasts = podcasts[:5]
        print("\n📋 Últimos 5 podcasts:")
        for podcast in recent_podcasts:
            print(f"  • {podcast['title']} ({podcast['date']})")
            print(f"    - URL: {podcast['url']}")
            print(f"    - Download: {podcast['download_url']}")
            if podcast["file_size"]:
                size_mb = podcast["file_size"] / (1024 * 1024)
                print(f"    - Tamaño: {size_mb:.1f} MB")
            else:
                print("    - Tamaño: No disponible")
            print()

    except Exception as e:
        print(f"❌ Error en la extracción completa: {e}")


if __name__ == "__main__":
    print("🧪 Iniciando pruebas de la nueva funcionalidad de links")

    # Ejecutar pruebas
    test_enhanced_link_extraction()
    test_database_integration()
    test_full_extraction()

    print("\n✅ Todas las pruebas completadas")
