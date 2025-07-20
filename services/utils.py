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

    # URLs de monetización que no queremos guardar
    monetization_urls = [
        "ko-fi.com/popcasting",
        "buymeacoffee.com/popcasting",
        "ko-fi.com",
        "buymeacoffee.com",
    ]

    # Buscar todas las URLs primero
    all_urls = set(re.findall(r"https?://[^\s]+", description))

    for url in all_urls:
        if any(monetization_url in url for monetization_url in monetization_urls):
            continue
        url_start = description.find(url)
        # Buscar el texto descriptivo que precede a la URL
        text_end = url_start
        # Ignorar ':' y espacios justo antes de la URL
        while text_end > 0 and description[text_end - 1] in ": ":
            text_end -= 1
        # Buscar el inicio del texto descriptivo
        text_start = 0
        for i in range(text_end - 1, -1, -1):
            char = description[i]
            if char in ["/", "|", "\n"] or description[i : i + 2] == "::":
                text_start = i + 1
                break
        text = description[text_start:text_end].strip()
        text = re.sub(r"^[:\s/|]+", "", text)
        text = re.sub(r"[:\s/|]+$", "", text)
        if not text:
            text = url
        extra_links.append({"text": text, "url": url})
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

    # Detectar si es formato numerado (00, 01, 02, etc.)
    if re.search(r"\b\d{2}\s+[^•]+?\s*•\s*[^0-9]+?(?=\s+\d{2}\s+|$)", description):
        if logger:
            logger.info(
                f"{program_info} - Detectado formato numerado, usando parser específico"
            )
        return parse_numbered_playlist_format(description, program_info, logger)

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
                                        "title": cleaned_song,
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
                                            "title": cleaned_song,
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
                                    "title": cleaned_song,
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
                                        "title": part.strip(),
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
                                        "title": "#corregir",
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
                                                    "title": cleaned_song,
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


def parse_numbered_playlist_format(
    text: str, program_info: str = "N/A", logger=None
) -> list[dict]:
    """
    Parser específico para el formato de canciones numeradas (00, 01, 02, etc.)
    que aparece en algunos episodios problemáticos.

    Args:
        text: Texto de la descripción del episodio
        program_info: Identificador del programa para logging
        logger: Logger opcional para registrar errores

    Returns:
        Lista de canciones con posición, artista y título
    """
    if not text:
        return []

    playlist = []

    # Patrón para encontrar canciones numeradas: 00 artista • canción 01 artista • canción
    # Buscar patrones como "00 charles cave • this fucking time of the year 01 suzie • sweet surprise"
    # También maneja casos donde el artista está separado: "00 phil collins" + "the roof is leaking (demo) 01 phil collins - i missed again"
    numbered_pattern = r"(\d{2})\s+([^•\n]+?)\s*[•-]\s*([^0-9]+?)(?=\s+\d{2}\s+|$)"

    matches = re.findall(numbered_pattern, text, re.DOTALL)

    for match in matches:
        number = match[0]
        artist = clean_text(match[1].strip())
        song = clean_text(match[2].strip())

        # Validar que tanto artista como canción no estén vacíos
        if artist and song and len(song) > 2:
            # Limpiar y validar la entrada
            cleaned_artist, cleaned_song = clean_song_info(artist, song)
            if validate_song_entry(cleaned_artist, cleaned_song):
                playlist.append(
                    {
                        "position": int(number),
                        "artist": cleaned_artist,
                        "title": cleaned_song,
                    }
                )
            else:
                error_msg = f"Entrada numerada inválida descartada: '{number} {artist} • {song}'"
                if logger:
                    logger.warning(f"{program_info} - {error_msg}")
                else:
                    print(f"AVISO {program_info}: {error_msg}")

    return playlist


def detect_and_clean_mixed_song_data(
    song_title: str, song_artist: str, extra_links: list
) -> tuple:
    """
    Detecta y limpia cuando las descripciones de enlaces extras se han mezclado
    con la información de la canción.

    Args:
        song_title: Título de la canción (posiblemente contaminado)
        song_artist: Artista de la canción (posiblemente contaminado)
        extra_links: Lista de enlaces extras extraídos del episodio

    Returns:
        tuple: (clean_title, clean_artist, link_descriptions)
    """
    # Combinar título y artista para análisis
    combined_text = f"{song_title} | {song_artist}"

    # Extraer las URLs de los enlaces extras
    [link["url"] for link in extra_links]

    # Patrones comunes de descripciones de enlaces extras
    link_patterns = [
        r"bongo joe records",
        r"ceints de bakélite",
        r"loud women",
        r"colour me wednesday",
        r"weird herald",
        r"miqui puig",
        r"invita a popcasting",
        r"ko-fi\.com",
        r"buymeacoffee\.com",
    ]

    # Buscar patrones de enlaces extras en el texto combinado
    found_descriptions = []
    clean_text = combined_text

    for pattern in link_patterns:
        if re.search(pattern, clean_text, re.IGNORECASE):
            # Extraer el texto alrededor del patrón
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                # Buscar el contexto completo (desde el separador anterior hasta el siguiente)
                start_pos = match.start()
                end_pos = match.end()

                # Buscar separadores antes y después
                before_sep = clean_text.rfind("|", 0, start_pos)
                after_sep = clean_text.find("|", end_pos)

                if before_sep != -1:
                    start_pos = before_sep + 1
                if after_sep != -1:
                    end_pos = after_sep

                description = clean_text[start_pos:end_pos].strip()
                found_descriptions.append(description)

                # Remover esta descripción del texto limpio
                clean_text = clean_text[:start_pos] + clean_text[end_pos:].lstrip("| ")

    # Limpiar separadores múltiples y espacios
    clean_text = re.sub(r"\|\s*\|", "|", clean_text)
    clean_text = re.sub(r"\|\s*$", "", clean_text)
    clean_text = re.sub(r"^\|\s*", "", clean_text)
    clean_text = clean_text.strip()

    # Separar título y artista del texto limpio
    parts = clean_text.split("|")
    if len(parts) >= 2:
        clean_title = parts[0].strip()
        clean_artist = parts[1].strip()
    else:
        # Si no hay separador, intentar separar por el patrón "título · artista"
        if " · " in clean_text:
            title_parts = clean_text.split(" · ")
            clean_title = title_parts[0].strip()
            clean_artist = title_parts[1].strip()
        else:
            # Si no hay separador, intentar extraer el artista del texto original
            # Buscar patrones como "título artista" donde artista es conocido
            if song_artist and song_artist in clean_text:
                # Remover el artista del título
                clean_title = clean_text.replace(song_artist, "").strip()
                clean_artist = song_artist
            else:
                # Si no hay separador, asumir que todo es título
                clean_title = clean_text
                clean_artist = ""

    # Si el título limpio está vacío, usar el artista original
    if not clean_title and song_artist:
        clean_title = song_artist
        clean_artist = ""

    return clean_title, clean_artist, found_descriptions


def update_song_with_clean_data(song_id: int, clean_title: str, clean_artist: str):
    """Actualiza una canción con datos limpios."""
    from services.database import get_db_connection

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE songs SET title = ?, artist = ? WHERE id = ?",
        (clean_title, clean_artist, song_id),
    )

    conn.commit()
    conn.close()


def update_extra_link_with_description(link_id: int, description: str):
    """Actualiza un enlace extra con su descripción correcta."""
    from services.database import get_db_connection

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "UPDATE extra_links SET text = ? WHERE id = ?", (description, link_id)
    )

    conn.commit()
    conn.close()


def match_descriptions_to_links(descriptions: list, extra_links: list) -> dict:
    """
    Asigna descripciones a enlaces basándose en coincidencias de contenido.

    Args:
        descriptions: Lista de descripciones encontradas
        extra_links: Lista de enlaces extras con sus URLs

    Returns:
        dict: Mapeo de link_id -> description
    """
    matches = {}

    # Mapeos conocidos de descripciones a dominios/patrones
    description_patterns = {
        "bongo joe records": ["bongojoe", "bongo"],
        "ceints de bakélite": ["ceintsdebakelite", "ceints"],
        "loud women": ["loudwomen", "loud"],
        "colour me wednesday": ["colourmewednesday", "colour"],
        "weird herald": ["weirdherald", "weird"],
        "miqui puig": ["miquipuig", "miqui"],
        "invita a popcasting": ["ko-fi", "buymeacoffee", "popcasting"],
    }

    # Para cada descripción, buscar el enlace que mejor coincida
    for description in descriptions:
        best_match = None
        best_score = 0

        for link in extra_links:
            url = link["url"].lower()
            score = 0

            # Buscar patrones específicos para esta descripción
            if description in description_patterns:
                for pattern in description_patterns[description]:
                    if pattern in url:
                        score += 10  # Coincidencia fuerte
                        break

            # Coincidencia directa de palabras clave
            words = description.lower().split()
            for word in words:
                if word in url:
                    score += 1

            if score > best_score:
                best_score = score
                best_match = link["id"]

        if best_match and best_match not in matches.values():
            matches[best_match] = description

    return matches
