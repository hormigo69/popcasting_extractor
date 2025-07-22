#!/usr/bin/env python3
"""
from pathlib import Path

Script rápido para encontrar el episodio #62 en el HTML.
"""


def find_episode_62_quick():
    """
    Busca rápidamente el episodio #62 en el archivo HTML.
    """
    html_file = Path("data/42-63.html")

    if not html_file.exists():
        print(f"❌ Archivo {html_file} no encontrado")
        return None

    print(f"📄 Buscando episodio #62 en {html_file}...")

    # Leer el archivo línea por línea para ser más eficiente
    with open(html_file, encoding="utf-8") as f:
        lines = f.readlines()

    # Buscar líneas que contengan "programa #62"
    episode_lines = []
    for i, line in enumerate(lines):
        if "programa #62" in line.lower():
            episode_lines.append((i, line.strip()))

    if not episode_lines:
        print("❌ No se encontró 'programa #62' en el archivo")
        return None

    print(f"✅ Encontradas {len(episode_lines)} líneas con 'programa #62'")

    # Mostrar las líneas encontradas
    for i, (line_num, line) in enumerate(episode_lines):
        print(f"\n📋 Línea {line_num + 1}:")
        print(f"   {line[:100]}...")

    # Buscar la playlist en las líneas siguientes
    for line_num, line in episode_lines:
        print(f"\n🔍 Analizando línea {line_num + 1}...")

        # Buscar el patrón de playlist en esta línea y las siguientes
        for j in range(line_num, min(line_num + 10, len(lines))):
            current_line = lines[j]

            # Buscar patrones de playlist
            if "[" in current_line and "]" in current_line:
                # Extraer contenido entre corchetes
                start = current_line.find("[")
                end = current_line.find("]")
                if start != -1 and end != -1 and end > start:
                    playlist_text = current_line[start + 1 : end].strip()
                    print(f"🎵 Playlist encontrada en línea {j + 1}:")
                    print(f"   {playlist_text}")

                    # Extraer canciones
                    songs = []
                    parts = playlist_text.split("::")

                    for k, part in enumerate(parts):
                        part = part.strip()
                        if part:
                            # Intentar separar artista y título
                            if " · " in part:
                                artist, title = part.split(" · ", 1)
                            elif " - " in part:
                                artist, title = part.split(" - ", 1)
                            else:
                                artist = part
                                title = ""

                            songs.append(
                                {
                                    "position": k + 1,
                                    "artist": artist.strip(),
                                    "title": title.strip(),
                                }
                            )

                    print(f"\n📋 Canciones extraídas ({len(songs)}):")
                    for song in songs:
                        print(
                            f"  {song['position']:2d}. {song['artist']} - {song['title']}"
                        )

                    return songs

    print("❌ No se pudo extraer la playlist del episodio #62")
    return None


def main():
    """Función principal del script."""
    print("🔍 Buscador rápido del episodio #62")
    print("=" * 40)

    songs = find_episode_62_quick()

    if songs:
        print("\n✅ Playlist del episodio #62 extraída exitosamente")
        print(f"🎵 Total de canciones: {len(songs)}")
    else:
        print("\n❌ No se pudo extraer la playlist")


if __name__ == "__main__":
    main()
