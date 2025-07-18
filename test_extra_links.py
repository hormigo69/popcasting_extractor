#!/usr/bin/env python3
"""
Script de prueba para verificar la extracción de links extras
"""

import os
import sys

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.utils import extract_extra_links


def test_extra_links_extraction():
    """Prueba la extracción de links extras con ejemplos reales"""

    # Ejemplo del TODO
    test_description = ":::::: weird herald https://weirdherald.bandcamp.com/album/just-yesterday :::::: yo no quería ser miqui puig https://miquipuig.com/author/miqui-admin-puig-web/ :::::: invita a Popcasting a café https://ko-fi.com/popcasting ]]>"

    # Ejemplo con variaciones de separadores
    test_description2 = "artista1 - cancion1 :: artista2 - cancion2 :: weird herald https://weirdherald.bandcamp.com/album/just-yesterday / yo no quería ser miqui puig https://miquipuig.com/author/miqui-admin-puig-web/"

    print("=== PRUEBA 1: Ejemplo del TODO ===")
    links1 = extract_extra_links(test_description)
    print(f"Links encontrados: {len(links1)}")
    for i, link in enumerate(links1, 1):
        print(f"  {i}. Texto: '{link['text']}'")
        print(f"     URL: {link['url']}")

    print("\n=== PRUEBA 2: Con variaciones de separadores ===")
    links2 = extract_extra_links(test_description2)
    print(f"Links encontrados: {len(links2)}")
    for i, link in enumerate(links2, 1):
        print(f"  {i}. Texto: '{link['text']}'")
        print(f"     URL: {link['url']}")

    print("\n=== PRUEBA 3: Sin links ===")
    test_description3 = (
        "artista1 - cancion1 :: artista2 - cancion2 :: artista3 - cancion3"
    )
    links3 = extract_extra_links(test_description3)
    print(f"Links encontrados: {len(links3)}")

    print("\n=== PRUEBA 4: Solo links ===")
    test_description4 = "https://weirdherald.bandcamp.com/album/just-yesterday :: https://miquipuig.com/author/miqui-admin-puig-web/"
    links4 = extract_extra_links(test_description4)
    print(f"Links encontrados: {len(links4)}")
    for i, link in enumerate(links4, 1):
        print(f"  {i}. Texto: '{link['text']}'")
        print(f"     URL: {link['url']}")


if __name__ == "__main__":
    test_extra_links_extraction()
