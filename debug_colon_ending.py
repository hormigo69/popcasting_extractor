#!/usr/bin/env python3
"""
Script para debuggear el problema con links que terminan en :
"""

import os
import sys

# Añadir el directorio raíz al path para importar los módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.utils import extract_extra_links


def test_colon_ending_case():
    """Prueba el caso problemático con links que terminan en :"""

    # Caso problemático específico
    test_cases = [
        "::: song-poems: https://shorturl.at/bQZ07 ::::",
        ":::::: weird herald https://weirdherald.bandcamp.com/album/just-yesterday :::::: yo no quería ser miqui puig https://miquipuig.com/author/miqui-admin-puig-web/ :::::: invita a Popcasting a café https://ko-fi.com/popcasting ]]>",
        "song-poems: https://shorturl.at/bQZ07",
        "texto descriptivo: https://ejemplo.com/link",
        "https://ejemplo.com/link: texto descriptivo",
        "texto descriptivo https://ejemplo.com/link:",
    ]

    for i, test_case in enumerate(test_cases, 1):
        print(f"\n=== CASO DE PRUEBA {i} ===")
        print(f"Descripción: '{test_case}'")

        links = extract_extra_links(test_case)
        print(f"Links encontrados: {len(links)}")
        for j, link in enumerate(links, 1):
            print(f"  {j}. Texto: '{link['text']}'")
            print(f"     URL: {link['url']}")


if __name__ == "__main__":
    test_colon_ending_case()
