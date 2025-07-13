# Popcasting Extractor

Extractor de datos del podcast **Popcasting** que procesa el RSS para extraer información de episodios, playlists de canciones y enlaces.

## Características

- ✅ **Extracción completa**: 395 episodios desde programa 60 hasta 483 (2007-2025)
- ✅ **Parsing inteligente**: Playlists con formato `artista · canción :: artista · canción`
- ✅ **Manejo de errores**: Espacios faltantes, separadores malformados, etc.
- ✅ **Enlaces iVoox**: URLs de descarga directa y páginas web
- ✅ **Zona horaria**: Fechas normalizadas a Madrid (CET/CEST)
- ✅ **Múltiples fuentes**: RSS principal + fuentes alternativas
- ✅ **Separación inteligente**: Enlaces externos vs canciones (sin contaminación)
- ✅ **Deduplicación**: Elimina enlaces y contenido duplicado automáticamente
- ✅ **URLs limpias**: Corrección de URLs duplicadas y malformadas
- ✅ **Validación robusta**: Filtrado de entradas inválidas o incompletas
- ✅ **Estructura organizada**: JSON con campos específicos para cada tipo de contenido

## Estructura del JSON generado

```json
[
  {
    "program_number": "483",
    "title": "Popcasting483",
    "published": "Sat, 12 Jul 2025 09:54:03 +0200",
    "ivoox_download_url": "https://www.ivoox.com/popcasting483_mf_152795387_feed_1.mp3",
    "ivoox_web_url": "https://www.ivoox.com/popcasting483-audios-mp3_rf_152795387_1.html",
    "playlist": [
      {
        "position": 1,
        "artist": "boyd bennett",
        "song": "seventeen"
      },
      {
        "position": 2,
        "artist": "don julian & the meadowlarks",
        "song": "boogie woogie"
      }
    ],
    "extra_links": [
      {
        "url": "https://ejemplo.com",
        "text": "Enlace extra HTML"
      }
    ],
    "episode_external_links": [
      {
        "description": "obituario brian wilson",
        "url": "https://jenesaispop.com/2025/06/12/501210/brian-wilson-obituario",
        "type": "external_link"
      },
      {
        "description": "invita a Popcasting a café",
        "url": "https://ko-fi.com/popcasting",
        "type": "external_link"
      }
    ]
  }
]
```

## Instalación

1. Clona o descarga este repositorio
2. Asegúrate de tener Python 3.13+ instalado
3. Instala las dependencias usando `uv`:

```bash
uv add feedparser requests beautifulsoup4 lxml
```

## Uso

### Ejecución básica

```bash
uv run python hello.py
```

### CLI avanzado con opciones

```bash
# Extracción completa
uv run python services/cli.py

# Solo mostrar estadísticas
uv run python services/cli.py --stats

# Filtrar por programa específico
uv run python services/cli.py --program-number 483

# Filtrar por año
uv run python services/cli.py --year 2024

# Solo episodios con 15+ canciones
uv run python services/cli.py --min-songs 15

# Exportar solo playlists
uv run python services/cli.py --playlist-only

# Combinación de filtros con estadísticas
uv run python services/cli.py --stats --min-songs 20 --year 2024

# Archivo de salida personalizado
uv run python services/cli.py --output mi_archivo.json

# Ver ayuda completa
uv run python services/cli.py --help
```

### Ejecución directa del servicio

```bash
uv run python services/popcasting_extractor.py
```

## Estructura del proyecto

```
popcasting_extractor/
├── hello.py                    # Punto de entrada principal
├── services/
│   ├── __init__.py
│   ├── popcasting_extractor.py # Servicio principal de extracción
│   ├── utils.py                # Utilidades para procesamiento de texto
│   └── cli.py                  # CLI avanzado con filtros y opciones
├── outputs/                    # Directorio donde se guardan los JSON
├── pyproject.toml             # Configuración del proyecto
└── README.md                  # Este archivo
```

## Funcionalidades del extractor

### 🎵 Extracción de playlists

- **Formato estándar**: `artista · canción :: artista · canción`
- **Tolerancia a errores**: Espacios variables, separadores malformados
- **Numeración automática**: Posiciones secuenciales (1, 2, 3...)
- **Validación inteligente**: Filtra entradas inválidas o incompletas
- **Limpieza de texto**: Elimina caracteres especiales y numeración extra

### 🔗 Extracción de enlaces

#### Enlaces externos del episodio (`episode_external_links`)
- **Obituarios y artículos**: Marcados con múltiples `::::::` 
- **Invitaciones a café**: ko-fi, patreon, etc.
- **Enlaces especiales**: Contenido relacionado con el episodio
- **Deduplicación**: Sin enlaces repetidos

#### Enlaces iVoox
- **Descarga directa**: URLs de archivos MP3
- **Página web**: Enlaces a la página del episodio

#### Enlaces extra (`extra_links`)
- **Enlaces HTML**: Otros enlaces encontrados en la descripción
- **Filtrado inteligente**: Excluye enlaces ya procesados

### 🛠️ Manejo de errores y limpieza

- **Separadores**: Normalización de `::` y `·` con espacios variables
- **URLs duplicadas**: Corrección automática de URLs malformadas
- **Deduplicación**: Elimina contenido repetido del RSS
- **Validación**: Filtra entradas de canciones inválidas
- **HTML**: Procesamiento robusto de contenido HTML malformado
- **Zona horaria**: Conversión automática a Madrid (CET/CEST)

## Dependencias

- `feedparser`: Para parsear el RSS
- `requests`: Para realizar peticiones HTTP
- `beautifulsoup4`: Para parsear HTML
- `lxml`: Parser XML/HTML rápido

## Salida

Los archivos JSON se guardan en la carpeta `outputs/` con nombres que incluyen timestamp:

```
outputs/popcasting_episodes_20250713_184205.json  # Datos completos
outputs/playlists_20250713_184423.json           # Solo playlists
ejemplo_output.json                              # Archivo de ejemplo
```

### Formato de playlists simplificado

```json
[
  {
    "program_number": "483",
    "title": "Popcasting483",
    "published": "Sat, 12 Jul 2025 09:54:03 +0200",
    "songs": [
      {
        "position": 1,
        "artist": "boyd bennett",
        "song": "seventeen"
      },
      {
        "position": 2,
        "artist": "don julian & the meadowlarks", 
        "song": "boogie woogie"
      }
    ]
  }
]
```

## 🔧 Problemas resueltos

### Separación de enlaces y canciones
- **Antes**: Enlaces mezclados con títulos de canciones
- **Después**: Enlaces en campo específico `episode_external_links`

### Deduplicación automática  
- **Antes**: Enlaces duplicados por procesamiento múltiple del RSS
- **Después**: Sistema inteligente que elimina duplicados por URL

### URLs limpias
- **Antes**: `https://site.com/path/https://site.com/path` (duplicadas)
- **Después**: `https://site.com/path` (limpias y válidas)

### Detección robusta
- **Antes**: Enlaces no detectados en algunos episodios
- **Después**: Detección consistente con múltiples patrones

## Estadísticas

### 📊 Estadísticas de la última extracción

- **395 episodios** procesados (programa 60 → 483)
- **4,950 canciones** extraídas y validadas
- **18 años** de historia musical (2007-2025)
- **Enlaces externos** correctamente separados y deduplicados
- **URLs limpias** sin duplicaciones ni errores
- **0 duplicados** en enlaces o contenido

## 🚀 Rendimiento

- **Tiempo de procesamiento**: ~30-60 segundos para 395 episodios
- **Memoria**: Uso eficiente con procesamiento secuencial
- **Robustez**: Manejo de errores sin interrupciones
- **Escalabilidad**: Preparado para nuevos episodios automáticamente

## 🔍 Tipos de enlaces detectados

| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| `external_link` | Obituarios, artículos, contenido especial | jenesaispop.com |
| `coffee_invitation` | Invitaciones a ko-fi automáticamente detectadas | ko-fi.com/popcasting |
| `support_link` | Enlaces de apoyo general | patreon.com |
| `patreon` | Enlaces específicos de Patreon | patreon.com/popcasting |

## 📝 Notas técnicas

- **RSS múltiple**: Procesa solo el campo `description` para evitar duplicados
- **Regex avanzado**: Patrones flexibles para diferentes formatos
- **Validación**: Filtra automáticamente entradas inválidas
- **Encoding**: UTF-8 completo con caracteres especiales
- **JSON**: Formato legible con indentación para debugging

## 🤝 Contribución

Si encuentras errores en el formato del RSS o tienes sugerencias para mejorar el parsing:

1. **Issues**: Reporta problemas específicos con ejemplos
2. **Pull Requests**: Mejoras en el código con tests
3. **Sugerencias**: Nuevas funcionalidades o optimizaciones

## 📄 Licencia

Este proyecto está bajo licencia MIT. Libre para uso personal y comercial.
