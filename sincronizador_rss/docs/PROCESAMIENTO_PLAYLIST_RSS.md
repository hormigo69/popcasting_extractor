# Procesamiento de Playlist del RSS

## Descripción

El archivo `src/components/rss_data_processor.py` ha sido modificado para convertir automáticamente el campo `summary` del RSS (que contiene la playlist en formato de texto) a una estructura JSON estructurada antes de devolver los datos.

## Funcionalidad Implementada

### Método `_process_rss_playlist()`

Este método procesa la playlist del RSS siguiendo esta lógica:

1. **Limpieza inicial**: Elimina texto extra como el de Ko-fi y otros patrones no deseados
2. **División por canciones**: Divide el string por el separador `::`
3. **Iteración y división por partes**: Para cada canción:
   - La divide por el separador `·` para separar artista y título
   - Maneja espacios en blanco con `strip()`
4. **Construcción del JSON**: Crea una lista de diccionarios con:
   - `position`: índice del bucle + 1
   - `artist`: nombre del artista
   - `title`: título de la canción
5. **Resultado**: Devuelve un JSON string que se guardará en la base de datos

### Método `_clean_playlist_text()`

Limpia el texto de la playlist eliminando:
- Texto de Ko-fi (`:::::: invita a Popcasting a café https://ko-fi.com/popcasting`)
- Referencias a archivos (`@rss_data_processor.py`)
- Espacios extra y líneas vacías

### Método `_parse_song_text()`

Parsea el texto de una canción individual para extraer artista y título. Soporta múltiples formatos:
- `artista · título` (formato principal de Popcasting)
- `artista - título`
- `artista: título`
- `artista "título"`

## Ejemplos de Procesamiento

### Entrada (texto del RSS):
```
the beatles · rain  ::  the doors · wintertime love  ::  joni mitchell · don't interrupt the sorrow

:::::: invita a Popcasting a café https://ko-fi.com/popcasting
```

### Salida (JSON):
```json
[
  {
    "position": 1,
    "artist": "the beatles",
    "title": "rain"
  },
  {
    "position": 2,
    "artist": "the doors",
    "title": "wintertime love"
  },
  {
    "position": 3,
    "artist": "joni mitchell",
    "title": "don't interrupt the sorrow"
  }
]
```

## Integración

El procesamiento se integra automáticamente en el método `_process_single_entry()`, donde:

1. Se extrae el campo `summary` del RSS como `raw_rss_playlist`
2. Se procesa usando `_process_rss_playlist()`
3. El resultado JSON se guarda en el campo `rss_playlist` del episodio

## Beneficios

- **Estructura consistente**: Todas las playlists del RSS tienen el mismo formato JSON
- **Fácil consulta**: Se pueden hacer consultas específicas por artista o título
- **Compatibilidad**: Mantiene compatibilidad con el procesamiento existente de playlists web
- **Limpieza automática**: Elimina contenido no deseado automáticamente

## Validación

El procesamiento incluye validaciones para:
- Texto vacío o nulo
- Artistas y títulos con longitud mínima
- Filtrado de palabras clave no deseadas
- Manejo de errores con fallback a playlist vacía

## Pruebas

Se han realizado pruebas exitosas con ejemplos reales del RSS de Popcasting, confirmando que:
- Se extraen correctamente 22-26 canciones por episodio
- Se eliminan correctamente los textos de Ko-fi
- El formato JSON es válido y consistente
- Los artistas y títulos se parsean correctamente 