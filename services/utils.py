"""
Utilidades para el procesamiento de datos de Popcasting
"""

import re


def clean_text(text: str) -> str:
    """Limpia texto eliminando espacios extra y caracteres especiales"""
    if not text:
        return ""

    # Eliminar espacios extra
    text = re.sub(r"\s+", " ", text)

    # Eliminar caracteres de control
    text = re.sub(r"[\x00-\x1f\x7f-\x9f]", "", text)

    return text.strip()


def normalize_separators(text: str) -> str:
    """Normaliza separadores de playlist para manejar errores comunes"""
    # Normalizar :: con espacios variables
    text = re.sub(r"\s*::\s*", " :: ", text)

    # Normalizar · con espacios variables
    text = re.sub(r"\s*·\s*", " · ", text)

    # Normalizar • con espacios variables
    text = re.sub(r"\s*•\s*", " • ", text)

    # Manejar casos donde faltan espacios
    text = re.sub(r"::(?!\s)", ":: ", text)
    text = re.sub(r"(?<!\s)::", " ::", text)

    return text


def extract_program_info(title: str) -> dict[str, str | None]:
    """Extrae información del programa desde el título"""
    info = {"number": None, "season": None, "special": None}

    # Patrones para número de programa
    number_patterns = [
        r"Popcasting\s*(\d+)",  # Patrón específico para Popcasting 483 (con o sin espacio)
        r"Programa\s+(\d+)",
        r"#(\d+)",
        r"Ep\.?\s*(\d+)",
        r"Episodio\s+(\d+)",
        r"(\d+)º?\s*programa",
    ]

    for pattern in number_patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            info["number"] = match.group(1)
            break

    # Patrones para temporada
    season_patterns = [r"Temporada\s+(\d+)", r"T(\d+)", r"Season\s+(\d+)"]

    for pattern in season_patterns:
        match = re.search(pattern, title, re.IGNORECASE)
        if match:
            info["season"] = match.group(1)
            break

    # Detectar episodios especiales
    special_patterns = [r"especial", r"navidad", r"año\s+nuevo", r"verano", r"extra"]

    for pattern in special_patterns:
        if re.search(pattern, title, re.IGNORECASE):
            info["special"] = True
            break

    return info


def validate_song_entry(artist: str, song: str) -> bool:
    """Valida que una entrada de canción sea válida"""
    if not artist or not song:
        return False

    artist_clean = artist.strip()
    song_clean = song.strip()

    # Validar que la canción tenga al menos 2 caracteres
    if len(song_clean) < 2:
        return False

    # Casos especiales conocidos (solo si no están cubiertos por las reglas generales)
    # Nota: "?" y "q" ya están cubiertos por la regla de caracteres únicos, así que no necesitan excepción

    # Si el artista tiene solo 1 carácter, validar si es un artista legítimo
    if len(artist_clean) == 1:
        # Permitir cualquier carácter único EXCEPTO los que claramente no son artistas
        invalid_single_chars = [
            r"^[\.\)\]\}\>]$",  # Símbolos de puntuación de cierre
            r"^[^\w\?]$",  # Cualquier carácter que no sea alfanumérico o ?
        ]

        for pattern in invalid_single_chars:
            if re.match(pattern, artist_clean):
                return False

        # Si pasa las validaciones, es un artista válido de un carácter
        # (incluyendo números como "5" que podrían ser nombres de artistas)
        return True

    # Para artistas de 2+ caracteres, aplicar validaciones normales
    if len(artist_clean) < 2:
        return False

    # Filtrar entradas que parecen ser texto descriptivo
    invalid_patterns = [
        r"^\d+[\.\)]\s*$",  # Solo números
        r"^[^\w]*$",  # Solo caracteres especiales
        r"continuamos",
        r"seguimos",
        r"próxima",
        r"anterior",
    ]

    combined_text = f"{artist_clean} {song_clean}".lower()
    for pattern in invalid_patterns:
        if re.search(pattern, combined_text):
            return False

    return True


def clean_song_info(artist: str, song: str) -> tuple:
    """Limpia información de artista y canción"""
    # Limpiar artista
    artist = clean_text(artist)
    artist = re.sub(r"^\d+[\.\)]\s*", "", artist)  # Remover numeración

    # Solo remover paréntesis al final si no contienen información importante
    # No remover si contiene "ft", "feat", "featuring", "dub", "remix", etc.
    if not re.search(
        r"\([^)]*(?:ft|feat|featuring|dub|remix|by)[^)]*\)", artist, re.IGNORECASE
    ):
        artist = re.sub(r"\s*\([^)]*\)\s*$", "", artist)

    # Limpiar canción
    song = clean_text(song)

    # Solo remover paréntesis al final si no contienen información importante
    # No remover si contiene información de la canción
    if not re.search(
        r"\([^)]*(?:i know|light the lanterns|grand prix)[^)]*\)", song, re.IGNORECASE
    ):
        song = re.sub(r"\s*\([^)]*\)\s*$", "", song)

    return artist.strip(), song.strip()


def extract_links_and_clean_text(text: str) -> (str, list[dict]):
    """
    Limpia el texto eliminando enlaces y frases basura.
    Ya no procesa enlaces externos como acordamos.
    """
    if not text:
        return "", []

    # Limpieza agresiva de frases conocidas que no son canciones
    text = re.sub(
        r"invita a popcasting a un? café\s*[:;·-]?\s*\)?", "", text, flags=re.IGNORECASE
    )
    text = re.sub(
        r"invita a popcasting a café\s*[:;·-]?\s*\)?", "", text, flags=re.IGNORECASE
    )
    text = re.sub(r"obituario.*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"libro.*?:", "", text, flags=re.IGNORECASE)
    text = re.sub(r"café\s*[:;·-]?\s*\)?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\)\s*$", "", text)  # Eliminar paréntesis sueltos al final

    # Eliminar enlaces HTTP/HTTPS completamente
    text = re.sub(r"https?://[^\s<]+", "", text, flags=re.IGNORECASE)

    # Limpiar separadores de enlaces que quedan sueltos
    text = re.sub(r"\s*::\s*", " ", text)
    text = re.sub(r"\s*\|\s*", " ", text)

    # Limpieza final de espacios extra
    text = re.sub(r"\s{2,}", " ", text).strip()

    return text, []


def extract_extra_links(description: str) -> list[dict]:
    """
    Extrae los links extras de la descripción del episodio.
    Los links están al final del campo description, separados por :::: o variaciones.

    Args:
        description: Texto de la descripción del episodio

    Returns:
        Lista de diccionarios con 'text' y 'url' de cada link extra
    """
    if not description:
        return []

    extra_links = []

    # Buscar patrones de texto + URL usando regex
    # Patrón 1: texto seguido de URL (con o sin separador)
    pattern1 = r"([^:\s]+(?:\s+[^:\s]+)*)\s*:?\s*(https?://[^\s]+)"

    # Patrón 2: URL seguida de texto (con o sin separador)
    pattern2 = r"(https?://[^\s]+)\s*:?\s*([^:\s]+(?:\s+[^:\s]+)*)"

    # Buscar todas las URLs primero para evitar duplicados
    all_urls = set(re.findall(r"https?://[^\s]+", description))

    # Buscar coincidencias con el primer patrón
    matches1 = re.findall(pattern1, description)
    for text, url in matches1:
        text = text.strip()
        if text and not text.startswith("http") and url in all_urls:
            extra_links.append({"text": text, "url": url})

    # Buscar coincidencias con el segundo patrón
    matches2 = re.findall(pattern2, description)
    for url, text in matches2:
        text = text.strip()
        if text and not text.startswith("http") and url in all_urls:
            extra_links.append({"text": text, "url": url})

    # Si no encontramos coincidencias con patrones, buscar URLs sueltas
    if not extra_links:
        for url in all_urls:
            extra_links.append({"text": url, "url": url})

    return extra_links


def detect_playlist_section(text: str) -> str | None:
    """Detecta y extrae la sección de playlist del texto"""
    # Patrones para identificar secciones de playlist
    section_patterns = [
        r"playlist[:\s]*(.*?)(?:\n\n|\Z)",
        r"canciones[:\s]*(.*?)(?:\n\n|\Z)",
        r"música[:\s]*(.*?)(?:\n\n|\Z)",
        r"tracklist[:\s]*(.*?)(?:\n\n|\Z)",
        r"temas[:\s]*(.*?)(?:\n\n|\Z)",
        r"sonamos[:\s]*(.*?)(?:\n\n|\Z)",
    ]

    for pattern in section_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()

    return None


def extract_timestamps(text: str) -> list[dict]:
    """Extrae timestamps de las canciones si están disponibles"""
    timestamps = []

    # Patrones para timestamps
    timestamp_patterns = [
        r"(\d{1,2}:\d{2})\s*[-–]\s*(.+)",
        r"(\d{1,2}:\d{2}:\d{2})\s*[-–]\s*(.+)",
        r"\[(\d{1,2}:\d{2})\]\s*(.+)",
        r"\((\d{1,2}:\d{2})\)\s*(.+)",
    ]

    lines = text.split("\n")
    for line in lines:
        for pattern in timestamp_patterns:
            match = re.search(pattern, line.strip())
            if match:
                timestamp = match.group(1)
                content = match.group(2).strip()

                timestamps.append({"timestamp": timestamp, "content": content})

    return timestamps


def parse_playlist_simple(
    description: str, program_info: str = "N/A", logger=None
) -> list[dict]:
    """
    Parser simplificado y efectivo para playlists de Popcasting.
    Basado en el enfoque de test pero integrado en la arquitectura actual.

    Args:
        description: Texto de la descripción del episodio
        program_info: Identificador del programa para logging
        logger: Logger opcional para registrar errores

    Returns:
        Lista de canciones con posición, artista y título
    """
    if not description:
        return []

    # Limpiar el texto de caracteres especiales y espacios
    description = clean_text(description)

    # Reemplazar caracteres especiales comunes
    description = description.replace("Â·", "·")
    description = description.replace("Â", "")
    description = description.replace("&amp;", "&")
    description = description.replace("&lt;", "<")
    description = description.replace("&gt;", ">")
    description = description.replace("&quot;", '"')

    # Remover enlaces y texto extra al final
    link_patterns = [
        r"https?://[^\s]+",
        r"::::+.*$",  # Múltiples dos puntos seguidos
        r"invita a popcasting.*$",
        r"flor de pasión.*$",
        r"my favourite.*$",
        r"las felindras.*$",
        r"revisionist history.*$",
        r"ko-fi\.com.*$",
        r"youtu\.be.*$",
    ]

    for pattern in link_patterns:
        description = re.sub(pattern, "", description, flags=re.IGNORECASE)

    # Normalizar separadores
    description = normalize_separators(description)

    # Dividir por el separador principal ::
    parts = description.split(" :: ")

    playlist = []
    position = 1

    for part in parts:
        part = clean_text(part)
        if not part or len(part) < 3:
            continue

        # Verificar si la parte contiene el separador artista-canción (· o •)
        if " · " in part or " • " in part:
            try:
                # Dividir en artista y canción (solo en el primer separador)
                if " · " in part:
                    artist, song = part.split(" · ", 1)
                else:
                    artist, song = part.split(" • ", 1)
                artist = clean_text(artist)
                song = clean_text(song)

                # Verificar que tanto artista como canción no estén vacíos
                if artist and song:
                    # Verificar que no sean enlaces o texto extraño
                    if not any(
                        x in artist.lower() for x in ["http", "www", ".com", "::::"]
                    ):
                        if not any(
                            x in song.lower() for x in ["http", "www", ".com", "::::"]
                        ):
                            # Limpiar y validar la entrada
                            cleaned_artist, cleaned_song = clean_song_info(artist, song)
                            if validate_song_entry(cleaned_artist, cleaned_song):
                                playlist.append(
                                    {
                                        "position": position,
                                        "artist": cleaned_artist,
                                        "song": cleaned_song,
                                    }
                                )
                                position += 1
                            else:
                                # Log de entrada inválida
                                error_msg = (
                                    f"Entrada inválida descartada: '{artist} · {song}'"
                                )
                                if logger:
                                    logger.warning(f"{program_info} - {error_msg}")
                                else:
                                    print(f"AVISO {program_info}: {error_msg}")

            except ValueError:
                # Si hay múltiples separadores en la parte, tomar solo la primera división
                if " · " in part:
                    parts_split = part.split(" · ")
                else:
                    parts_split = part.split(" • ")
                if len(parts_split) >= 2:
                    artist = clean_text(parts_split[0])
                    # Reconstruir la canción con el separador original
                    if " · " in part:
                        song = clean_text(" · ".join(parts_split[1:]))
                    else:
                        song = clean_text(" • ".join(parts_split[1:]))

                    if artist and song:
                        if not any(
                            x in artist.lower() for x in ["http", "www", ".com", "::::"]
                        ):
                            if not any(
                                x in song.lower()
                                for x in ["http", "www", ".com", "::::"]
                            ):
                                cleaned_artist, cleaned_song = clean_song_info(
                                    artist, song
                                )
                                if validate_song_entry(cleaned_artist, cleaned_song):
                                    playlist.append(
                                        {
                                            "position": position,
                                            "artist": cleaned_artist,
                                            "song": cleaned_song,
                                        }
                                    )
                                    position += 1
                                else:
                                    error_msg = f"Entrada inválida descartada: '{artist} · {song}'"
                                    if logger:
                                        logger.warning(f"{program_info} - {error_msg}")
                                    else:
                                        print(f"AVISO {program_info}: {error_msg}")
        else:
            # Si no tiene separador artista-canción, analizar casos especiales
            if not any(
                x in part.lower() for x in ["http", "www", ".com", "::::", "invita a"]
            ):
                if len(part) > 3 and len(part) < 200:  # Longitud razonable
                    # Caso 1: Detectar si es "artista canción" sin separador
                    # Intentar dividir por la mitad
                    words = part.split()
                    if len(words) >= 2:
                        # Asumir que las primeras palabras son el artista
                        mid_point = len(words) // 2
                        artist = " ".join(words[:mid_point])
                        song = " ".join(words[mid_point:])

                        cleaned_artist, cleaned_song = clean_song_info(artist, song)
                        if validate_song_entry(cleaned_artist, cleaned_song):
                            playlist.append(
                                {
                                    "position": position,
                                    "artist": cleaned_artist,
                                    "song": cleaned_song,
                                }
                            )
                            position += 1
                        else:
                            # Caso 2: Intentar detectar patrones específicos
                            processed = False

                            # Patrón: "mysterious song (light the lanterns?)" - es título
                            if (
                                "mysterious song" in part.lower()
                                or "(" in part
                                and ")" in part
                            ):
                                # Parece ser un título, poner en título y artista como #corregir
                                playlist.append(
                                    {
                                        "position": position,
                                        "artist": "#corregir",
                                        "song": part.strip(),
                                    }
                                )
                                position += 1
                                processed = True

                            # Patrón: "the chieftains (ft marianne faithfull)" - es artista
                            elif "ft " in part.lower() or "feat" in part.lower():
                                # Parece ser un artista con featuring, poner en artista y título como #corregir
                                playlist.append(
                                    {
                                        "position": position,
                                        "artist": part.strip(),
                                        "song": "#corregir",
                                    }
                                )
                                position += 1
                                processed = True

                            # Si no se procesó con patrones específicos, intentar división simple
                            if not processed:
                                # Intentar dividir por la primera palabra que parece ser artista
                                words = part.split()
                                if len(words) >= 2:
                                    # Buscar palabras que parecen ser nombres de artistas
                                    artist_indicators = [
                                        "the",
                                        "ft",
                                        "feat",
                                        "featuring",
                                    ]
                                    artist_end = 1

                                    for i, word in enumerate(words):
                                        if word.lower() in artist_indicators or i < 2:
                                            artist_end = i + 1
                                        else:
                                            break

                                    if artist_end < len(words):
                                        artist = " ".join(words[:artist_end])
                                        song = " ".join(words[artist_end:])

                                        cleaned_artist, cleaned_song = clean_song_info(
                                            artist, song
                                        )
                                        if validate_song_entry(
                                            cleaned_artist, cleaned_song
                                        ):
                                            playlist.append(
                                                {
                                                    "position": position,
                                                    "artist": cleaned_artist,
                                                    "song": cleaned_song,
                                                }
                                            )
                                            position += 1
                                            processed = True

                            # Si aún no se procesó, registrar como error
                            if not processed:
                                error_msg = (
                                    f"Entrada sin separador descartada: '{part}'"
                                )
                                if logger:
                                    logger.warning(f"{program_info} - {error_msg}")
                                else:
                                    print(f"AVISO {program_info}: {error_msg}")

    return playlist
