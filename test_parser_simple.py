#!/usr/bin/env python3
"""
Script de prueba simple para el parser de playlists
"""

import re
from typing import List, Dict

def clean_text(text: str) -> str:
    """Limpia texto eliminando espacios extra y caracteres especiales"""
    if not text:
        return ""
    
    # Eliminar espacios extra
    text = re.sub(r'\s+', ' ', text)
    
    # Eliminar caracteres de control
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', text)
    
    return text.strip()

def normalize_separators(text: str) -> str:
    """Normaliza separadores de playlist para manejar errores comunes"""
    # Normalizar :: con espacios variables
    text = re.sub(r'\s*::\s*', ' :: ', text)
    
    # Normalizar · con espacios variables
    text = re.sub(r'\s*·\s*', ' · ', text)
    
    # Manejar casos donde faltan espacios
    text = re.sub(r'::(?!\s)', ':: ', text)
    text = re.sub(r'(?<!\s)::', ' ::', text)
    
    return text

def validate_song_entry(artist: str, song: str) -> bool:
    """Valida que una entrada de canción sea válida"""
    if not artist or not song:
        return False
    
    # Filtrar entradas muy cortas
    if len(artist.strip()) < 2 or len(song.strip()) < 2:
        return False
    
    # Filtrar entradas que parecen ser texto descriptivo
    invalid_patterns = [
        r'^\d+[\.\)]\s*$',  # Solo números
        r'^[^\w]*$',        # Solo caracteres especiales
        r'continuamos',
        r'seguimos',
        r'próxima',
        r'anterior'
    ]
    
    combined_text = f"{artist} {song}".lower()
    for pattern in invalid_patterns:
        if re.search(pattern, combined_text):
            return False
    
    return True

def clean_song_info(artist: str, song: str) -> tuple:
    """Limpia información de artista y canción"""
    # Limpiar artista
    artist = clean_text(artist)
    artist = re.sub(r'^\d+[\.\)]\s*', '', artist)  # Remover numeración
    artist = re.sub(r'\s*\([^)]*\)\s*$', '', artist)  # Remover info entre paréntesis
    
    # Limpiar canción
    song = clean_text(song)
    song = re.sub(r'\s*\([^)]*\)\s*$', '', song)  # Remover info entre paréntesis al final
    
    return artist.strip(), song.strip()

def parse_playlist_simple(description: str, program_info: str = "N/A") -> List[Dict]:
    """
    Parser simplificado y efectivo para playlists de Popcasting.
    Basado en el enfoque de test pero integrado en la arquitectura actual.
    """
    if not description:
        return []
    
    # Limpiar el texto de caracteres especiales y espacios
    description = clean_text(description)
    
    # Reemplazar caracteres especiales comunes
    description = description.replace('Â·', '·')
    description = description.replace('Â', '')
    description = description.replace('&amp;', '&')
    description = description.replace('&lt;', '<')
    description = description.replace('&gt;', '>')
    description = description.replace('&quot;', '"')
    
    # Remover enlaces y texto extra al final
    link_patterns = [
        r'https?://[^\s]+',
        r'::::+.*$',  # Múltiples dos puntos seguidos
        r'invita a popcasting.*$',
        r'flor de pasión.*$',
        r'my favourite.*$',
        r'las felindras.*$',
        r'revisionist history.*$',
        r'ko-fi\.com.*$',
        r'youtu\.be.*$'
    ]
    
    for pattern in link_patterns:
        description = re.sub(pattern, '', description, flags=re.IGNORECASE)
    
    # Normalizar separadores
    description = normalize_separators(description)
    
    # Dividir por el separador principal ::
    parts = description.split(' :: ')
    
    playlist = []
    position = 1
    
    for part in parts:
        part = clean_text(part)
        if not part or len(part) < 3:
            continue
            
        # Verificar si la parte contiene el separador artista-canción
        if ' · ' in part:
            try:
                # Dividir en artista y canción (solo en el primer ·)
                artist, song = part.split(' · ', 1)
                artist = clean_text(artist)
                song = clean_text(song)
                
                # Verificar que tanto artista como canción no estén vacíos
                if artist and song:
                    # Verificar que no sean enlaces o texto extraño
                    if not any(x in artist.lower() for x in ['http', 'www', '.com', '::::']):
                        if not any(x in song.lower() for x in ['http', 'www', '.com', '::::']):
                            # Limpiar y validar la entrada
                            cleaned_artist, cleaned_song = clean_song_info(artist, song)
                            if validate_song_entry(cleaned_artist, cleaned_song):
                                playlist.append({
                                    "position": position,
                                    "artist": cleaned_artist,
                                    "song": cleaned_song
                                })
                                position += 1
                            else:
                                # Log de entrada inválida
                                print(f"AVISO {program_info}: Entrada inválida descartada: '{artist} · {song}'")
                                
            except ValueError:
                # Si hay múltiples ' · ' en la parte, tomar solo la primera división
                parts_split = part.split(' · ')
                if len(parts_split) >= 2:
                    artist = clean_text(parts_split[0])
                    song = clean_text(' · '.join(parts_split[1:]))
                    
                    if artist and song:
                        if not any(x in artist.lower() for x in ['http', 'www', '.com', '::::']):
                            if not any(x in song.lower() for x in ['http', 'www', '.com', '::::']):
                                cleaned_artist, cleaned_song = clean_song_info(artist, song)
                                if validate_song_entry(cleaned_artist, cleaned_song):
                                    playlist.append({
                                        "position": position,
                                        "artist": cleaned_artist,
                                        "song": cleaned_song
                                    })
                                    position += 1
                                else:
                                    print(f"AVISO {program_info}: Entrada inválida descartada: '{artist} · {song}'")
        else:
            # Si no tiene separador artista-canción, podría ser texto extra
            # Solo incluir si parece ser una canción válida (no enlaces ni texto extraño)
            if not any(x in part.lower() for x in ['http', 'www', '.com', '::::', 'invita a']):
                if len(part) > 3 and len(part) < 200:  # Longitud razonable
                    # Intentar detectar si es "artista canción" sin separador
                    words = part.split()
                    if len(words) >= 2:
                        # Asumir que las primeras palabras son el artista
                        mid_point = len(words) // 2
                        artist = ' '.join(words[:mid_point])
                        song = ' '.join(words[mid_point:])
                        
                        cleaned_artist, cleaned_song = clean_song_info(artist, song)
                        if validate_song_entry(cleaned_artist, cleaned_song):
                            playlist.append({
                                "position": position,
                                "artist": cleaned_artist,
                                "song": cleaned_song
                            })
                            position += 1
                        else:
                            print(f"AVISO {program_info}: Entrada sin separador descartada: '{part}'")
    
    return playlist

def test_parser():
    """Prueba el parser con ejemplos conocidos"""
    
    # Ejemplo del episodio 317 que tenía problemas
    test_description_317 = """
    yyxy · love4eva  :: en attendant ana · the violence inside  :: young scum · freak out :: bob dylan · simple twist of fate  :: pi ja ma · ponytail :: let's eat grandma · falling into me ::  evie sands · one fine summer morning :: the sadies · a good flying day  :: bruno mars · magic :: jean-françois coen · vive l'amour :: bobbie gentry · thunder in the afternoon  :: véronique jannot & laurent voulzy · désir désir :: kelley stoltz · where you will :: chic · i want your love  :: mcguinn clark & hillman · surrender to me :: melenas · gira :: the goon sax · time 4 love :: las felindras · françoise implose  :: dusk · leaf :: elvis presley · are you lonesome tonight? (live) :: chin up · the rhythm method :: tristen · glass jar :: maki asakawa · konna fu ni sugite iku  ::  sugar and tiger · perruque rose :: alger patcho · rocky patcho :: módulos · nada me importa :: betty troupe · ms 20 :: bmx bandits · I can't stand mad at you  :: bombón · i wanna surf like anette :: daddy issues · all my girls :: scott mannion · the substance that i can't live without
    """
    
    # Ejemplo con enlaces al final
    test_description_with_links = """
    boyd bennett · seventeen :: don julian & the meadowlarks · boogie woogie :: invita a Popcasting a café https://ko-fi.com/popcasting
    """
    
    # Ejemplo con caracteres especiales
    test_description_special_chars = """
    artistÂ·song :: anotherÂ·artistÂ·anotherÂ·song :: normal artist · normal song
    """
    
    print("🧪 Probando el nuevo parser simplificado...\n")
    
    # Prueba 1: Episodio 317
    print("📻 Prueba 1: Episodio 317 (caso problemático)")
    playlist_317 = parse_playlist_simple(test_description_317, "Episodio 317")
    print(f"   Canciones encontradas: {len(playlist_317)}")
    for i, song in enumerate(playlist_317[:5]):
        print(f"   {i+1}. {song['artist']} · {song['song']}")
    if len(playlist_317) > 5:
        print(f"   ... y {len(playlist_317) - 5} más")
    print()
    
    # Prueba 2: Con enlaces
    print("🔗 Prueba 2: Con enlaces al final")
    playlist_links = parse_playlist_simple(test_description_with_links, "Episodio con enlaces")
    print(f"   Canciones encontradas: {len(playlist_links)}")
    for song in playlist_links:
        print(f"   - {song['artist']} · {song['song']}")
    print()
    
    # Prueba 3: Caracteres especiales
    print("🔤 Prueba 3: Caracteres especiales")
    playlist_special = parse_playlist_simple(test_description_special_chars, "Episodio con caracteres especiales")
    print(f"   Canciones encontradas: {len(playlist_special)}")
    for song in playlist_special:
        print(f"   - {song['artist']} · {song['song']}")
    print()
    
    # Prueba 4: Caso vacío
    print("❌ Prueba 4: Descripción vacía")
    playlist_empty = parse_playlist_simple("", "Episodio vacío")
    print(f"   Canciones encontradas: {len(playlist_empty)}")
    print()
    
    # Prueba 5: Solo enlaces
    print("🔗 Prueba 5: Solo enlaces")
    playlist_only_links = parse_playlist_simple("https://ko-fi.com/popcasting :: https://youtu.be/example", "Solo enlaces")
    print(f"   Canciones encontradas: {len(playlist_only_links)}")
    print()
    
    print("✅ Pruebas completadas!")

if __name__ == "__main__":
    test_parser() 