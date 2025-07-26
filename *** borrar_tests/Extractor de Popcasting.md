# Extractor de Popcasting

Este programa extrae información de todos los episodios del podcast **Popcasting** desde su RSS y genera un archivo JSON con datos estructurados.

## Características

El programa extrae la siguiente información de cada episodio:

- **Número del programa**: Extraído del título (ej: Popcasting483 → 483)
- **URL web del episodio**: Enlace a la página de iVoox
- **URL de descarga**: Enlace directo al archivo MP3
- **Playlist completa**: Lista de canciones con:
  - Posición en la playlist
  - Artista
  - Canción
- **Enlaces extra**: URLs adicionales encontrados en la descripción
- **Metadatos**: Fecha de publicación, duración, GUID

## Archivos incluidos

- `popcasting_extractor.py`: Programa principal
- `show_stats.py`: Script para mostrar estadísticas del JSON generado
- `README.md`: Esta documentación
- `rss_analysis.md`: Análisis de la estructura del RSS

## Uso

### Extracción de datos

```bash
python3 popcasting_extractor.py
```

Este comando:
1. Descarga el RSS de Popcasting
2. Procesa todos los episodios
3. Genera el archivo `popcasting_data.json`

### Visualización de estadísticas

```bash
python3 show_stats.py
```

Muestra estadísticas detalladas del JSON generado.

## Estructura del JSON

```json
{
  "podcast_name": "Popcasting",
  "rss_url": "https://feeds.feedburner.com/Popcasting",
  "extraction_date": "2025-07-13T11:50:46.079140",
  "total_episodes": 395,
  "episodes": [
    {
      "title": "Popcasting483",
      "episode_number": 483,
      "web_url": "https://www.ivoox.com/popcasting483-audios-mp3_rf_152795387_1.html",
      "download_url": "https://www.ivoox.com/popcasting483_mf_152795387_feed_1.mp3?d=1752393173",
      "playlist": [
        {
          "position": 1,
          "artist": "boyd bennett",
          "song": "seventeen"
        }
      ],
      "extra_links": [
        {
          "text": "invita a Popcasting a café https://ko-fi.com/popcasting",
          "url": "https://ko-fi.com/popcasting"
        }
      ],
      "publication_date": "Sat, 12 Jul 2025 09:54:03 +0200",
      "duration": "01:57:10",
      "guid": "https://www.ivoox.com/152795387"
    }
  ]
}
```

## Estadísticas actuales

- **Total de episodios**: 395
- **Total de canciones**: 4,325
- **Total de enlaces extra**: 332
- **Rango de episodios**: Del 60 al 483
- **Promedio de canciones por episodio**: 10.9

## Requisitos

- Python 3.x
- Librerías estándar: `requests`, `xml.etree.ElementTree`, `json`, `re`, `datetime`

## Instalación de dependencias

```bash
pip3 install requests
```

## Notas técnicas

### Formato de las canciones en el RSS

Las canciones vienen en el formato:
```
artista · canción :: artista · canción :: ...
```

### Enlaces extra

Se detectan automáticamente URLs en la descripción que no forman parte de la playlist de canciones.

### Manejo de errores

El programa incluye manejo de errores para:
- Problemas de conexión al RSS
- Errores de parsing del XML
- Episodios con formato irregular

## Autor

Programa desarrollado para extraer datos del podcast Popcasting (https://feeds.feedburner.com/Popcasting)

