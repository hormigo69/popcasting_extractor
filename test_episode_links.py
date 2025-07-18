#!/usr/bin/env python3
"""
Script de prueba para analizar los links disponibles en el feed de Popcasting
"""

import feedparser
import requests
from bs4 import BeautifulSoup


def test_feed_links():
    """Prueba la extracción de links del feed RSS"""

    # URLs del feed a probar
    urls_to_try = [
        "https://feeds.feedburner.com/Popcasting",
        "https://www.ivoox.com/podcast-popcasting_fg_f1604_feedRSS_o.xml",
        "https://feeds.feedburner.com/Popcasting?format=xml",
    ]

    for url in urls_to_try:
        print(f"\n{'='*60}")
        print(f"Probando URL: {url}")
        print(f"{'='*60}")

        try:
            feed = feedparser.parse(url)

            if not feed.entries:
                print("❌ No se encontraron episodios")
                continue

            print(f"✅ Encontrados {len(feed.entries)} episodios")

            # Analizar los primeros 3 episodios en detalle
            for i, entry in enumerate(feed.entries[:3]):
                print(f"\n--- Episodio {i+1} ---")
                print(f"Título: {entry.get('title', 'Sin título')}")
                print(f"Fecha: {entry.get('published', 'Sin fecha')}")

                # Analizar links disponibles
                print("\n📎 Links encontrados:")

                # 1. Link principal del entry
                main_link = entry.get("link")
                if main_link:
                    print(f"  • Link principal: {main_link}")

                # 2. Links en entry.links
                if hasattr(entry, "links") and entry.links:
                    print(f"  • Links en entry.links ({len(entry.links)}):")
                    for j, link in enumerate(entry.links):
                        print(f"    {j+1}. href: {link.get('href', 'N/A')}")
                        print(f"       type: {link.get('type', 'N/A')}")
                        print(f"       rel: {link.get('rel', 'N/A')}")
                        print(f"       title: {link.get('title', 'N/A')}")

                # 3. Enclosures (archivos adjuntos)
                if hasattr(entry, "enclosures") and entry.enclosures:
                    print(f"  • Enclosures ({len(entry.enclosures)}):")
                    for j, enclosure in enumerate(entry.enclosures):
                        print(f"    {j+1}. href: {enclosure.get('href', 'N/A')}")
                        print(f"       type: {enclosure.get('type', 'N/A')}")
                        print(f"       length: {enclosure.get('length', 'N/A')}")

                # 4. Buscar links en la descripción
                description = entry.get("description", "")
                if description:
                    soup = BeautifulSoup(description, "html.parser")
                    links_in_desc = soup.find_all("a", href=True)
                    if links_in_desc:
                        print(f"  • Links en descripción ({len(links_in_desc)}):")
                        for j, link in enumerate(links_in_desc):
                            print(
                                f"    {j+1}. {link.get('href')} - {link.get_text()[:50]}..."
                            )

                # 5. Buscar links en el contenido
                if hasattr(entry, "content") and entry.content:
                    for content_item in entry.content:
                        content_value = content_item.get("value", "")
                        if content_value:
                            soup = BeautifulSoup(content_value, "html.parser")
                            links_in_content = soup.find_all("a", href=True)
                            if links_in_content:
                                print(
                                    f"  • Links en contenido ({len(links_in_content)}):"
                                )
                                for j, link in enumerate(links_in_content):
                                    print(
                                        f"    {j+1}. {link.get('href')} - {link.get_text()[:50]}..."
                                    )

                print("-" * 40)

        except Exception as e:
            print(f"❌ Error al procesar {url}: {e}")


def test_ivoox_web_scraping():
    """Prueba extraer información adicional de la web de iVoox"""
    print(f"\n{'='*60}")
    print("Probando extracción de información de la web de iVoox")
    print(f"{'='*60}")

    # URL de ejemplo de un episodio de Popcasting en iVoox
    test_url = (
        "https://www.ivoox.com/popcasting-2024-01-15-audios-mp3_rf_12345678_1.html"
    )

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }

        response = requests.get(test_url, headers=headers, timeout=10)
        print(f"Status code: {response.status_code}")

        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")

            # Buscar elementos específicos de iVoox
            print("\nElementos encontrados en la página:")

            # Título del episodio
            title_elem = soup.find("h1", class_="title")
            if title_elem:
                print(f"Título: {title_elem.get_text().strip()}")

            # Descripción
            desc_elem = soup.find("div", class_="description")
            if desc_elem:
                print(f"Descripción: {desc_elem.get_text()[:200]}...")

            # Links de descarga
            download_links = soup.find_all(
                "a", href=lambda x: x and ("download" in x or ".mp3" in x)
            )
            if download_links:
                print(f"Links de descarga encontrados: {len(download_links)}")
                for link in download_links:
                    print(f"  • {link.get('href')}")

            # Links de redes sociales
            social_links = soup.find_all(
                "a",
                href=lambda x: x
                and any(
                    social in x
                    for social in ["facebook", "twitter", "instagram", "youtube"]
                ),
            )
            if social_links:
                print(f"Links sociales encontrados: {len(social_links)}")
                for link in social_links:
                    print(f"  • {link.get('href')}")

        else:
            print(f"❌ No se pudo acceder a la página: {response.status_code}")

    except Exception as e:
        print(f"❌ Error al hacer scraping: {e}")


if __name__ == "__main__":
    print("🔍 Analizando links disponibles en el feed de Popcasting")
    test_feed_links()
    test_ivoox_web_scraping()
    print("\n✅ Análisis completado")
