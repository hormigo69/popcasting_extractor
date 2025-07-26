# Scripts de Scraping de Episodios

Este directorio contiene scripts para scrapear y buscar episodios específicos de Popcasting, combinando datos del RSS y WordPress.

## Scripts Disponibles

### 1. `scrape_episode.py` - Scrapear Episodio Específico

Scrapea un episodio específico por número, combinando datos del RSS y WordPress.

#### Uso Básico
```bash
# Scrapear episodio 485
python scrape_episode.py 485

# Scrapear episodio 100 y guardar en archivo
python scrape_episode.py 100 -o episodio_100.json

# Scrapear episodio 200 con información detallada
python scrape_episode.py 200 -v
```

#### Argumentos
- `episode_number`: Número del episodio a scrapear (obligatorio)
- `-o, --output`: Archivo de salida para guardar los datos en formato JSON
- `-v, --verbose`: Mostrar información detallada del episodio

#### Información Extraída
- **Datos del RSS**: título, fecha, duración, URL, playlist, etc.
- **Datos de WordPress**: contenido, extracto, categorías, tags, playlist web, etc.
- **Datos unificados**: combinación de ambas fuentes

### 2. `search_episode.py` - Buscar Episodios

Busca episodios por título, número exacto o rango de números.

#### Tipos de Búsqueda

##### Búsqueda por Título
```bash
# Buscar episodios que contengan "especial" en el título
python search_episode.py title "especial"

# Buscar episodios con "smash hits" y guardar resultados
python search_episode.py title "smash hits" -o especiales.json
```

##### Búsqueda por Número Exacto
```bash
# Buscar episodio número 485
python search_episode.py number 485

# Buscar episodio 100 con información detallada
python search_episode.py number 100 -v
```

##### Búsqueda por Rango
```bash
# Buscar episodios del 480 al 490
python search_episode.py range 480-490

# Buscar solo episodio 485 (equivalente a number 485)
python search_episode.py range 485
```

#### Argumentos
- `search_type`: Tipo de búsqueda (`title`, `number`, `range`)
- `search_value`: Valor a buscar
- `-o, --output`: Archivo de salida para guardar los resultados
- `-v, --verbose`: Mostrar información detallada

## Ejemplos de Uso

### Ejemplo 1: Scrapear un Episodio Específico
```bash
# Scrapear episodio 485 y guardar en archivo
python scrape_episode.py 485 -o episodio_485.json -v
```

**Salida esperada:**
```
🎯 Iniciando scrape del episodio 485
📋 Cargando configuración...
🔧 Inicializando procesadores...
📻 Descargando episodios del RSS...
📊 Encontrados 486 episodios en el RSS
🔍 Buscando episodio número 485...
✅ Episodio encontrado: Popcasting485
🔗 Enriqueciendo datos con WordPress...
📋 === INFORMACIÓN DEL EPISODIO ===
🎵 Título: Popcasting485
📅 Fecha: 2024-01-15
🔢 Número: 485
⏱️ Duración: 01:23:45
📁 Tamaño: 45.2 MB
🔗 URL: https://example.com/episodio-485
🌐 === DATOS DE WORDPRESS ===
🆔 WordPress ID: 12345
📝 Título WordPress: Popcasting 485 - Especial Año Nuevo
📄 Extracto: Un especial para celebrar el año nuevo...
🏷️ Categorías: Especiales, Pop
🏷️ Tags: año nuevo, especial, 2024
🎵 Playlist WordPress: 25 canciones
🎵 === INFORMACIÓN DE PLAYLISTS ===
📻 Playlist RSS: 25 canciones
🌐 Playlist Web: 25 canciones
💾 Guardando datos en episodio_485.json...
✅ Datos guardados en episodio_485.json
🎉 Scrape completado exitosamente
```

### Ejemplo 2: Buscar Episodios Especiales
```bash
# Buscar todos los episodios especiales
python search_episode.py title "especial" -v
```

**Salida esperada:**
```
🔍 Iniciando búsqueda de tipo: title
📋 Cargando configuración...
🔧 Inicializando procesador RSS...
📻 Descargando episodios del RSS...
📊 Encontrados 486 episodios en el RSS
🔍 Buscando episodios con título que contenga: 'especial'
📊 === RESULTADOS DE BÚSQUEDA ===
🔍 Tipo de búsqueda: title
🔍 Valor buscado: especial
✅ Episodios encontrados: 15
📋 === EPISODIOS ENCONTRADOS ===
1. 🎵 Popcasting195 (especial Smash Hits 1984)
   📅 2023-06-15 | 🔢 #195 | ⏱️ 01:45:30
   🔗 URL: https://example.com/episodio-195
   📁 Tamaño: 52.1 MB
   🎵 Canciones RSS: 30

2. 🎵 Popcasting485 (especial Año Nuevo)
   📅 2024-01-15 | 🔢 #485 | ⏱️ 01:23:45
   🔗 URL: https://example.com/episodio-485
   📁 Tamaño: 45.2 MB
   🎵 Canciones RSS: 25
```

### Ejemplo 3: Buscar Rango de Episodios
```bash
# Buscar episodios del 480 al 490
python search_episode.py range 480-490 -o rango_episodios.json
```

## Estructura de Datos

### Datos del RSS
- `title`: Título del episodio
- `date`: Fecha de publicación
- `program_number`: Número del programa
- `duration`: Duración del audio
- `file_size`: Tamaño del archivo
- `url`: URL del episodio
- `rss_playlist`: Playlist extraída del RSS

### Datos de WordPress
- `wordpress_id`: ID del post en WordPress
- `wordpress_title`: Título del post
- `wordpress_content`: Contenido completo
- `wordpress_excerpt`: Extracto
- `wordpress_categories`: Categorías
- `wordpress_tags`: Tags
- `wordpress_playlist_data`: Playlist estructurada
- `featured_image_url`: URL de la imagen destacada

### Datos Unificados
Los scripts combinan ambas fuentes, priorizando los datos de WordPress cuando están disponibles.

## Configuración

Los scripts utilizan la misma configuración que el sincronizador principal:
- `config.ini`: Configuración de RSS y WordPress
- Credenciales de Supabase (si se requieren)

## Requisitos

- Python 3.7+
- Dependencias del sincronizador RSS
- Acceso a la configuración del proyecto

## Notas Importantes

1. **Rendimiento**: Los scripts descargan todo el RSS para buscar episodios específicos. Para uso frecuente, considera cachear los datos.

2. **Datos de WordPress**: No todos los episodios tienen datos de WordPress disponibles. Los scripts funcionan con datos del RSS como fallback.

3. **Formato de Salida**: Los archivos JSON contienen todos los datos extraídos en formato estructurado.

4. **Logging**: Los scripts utilizan el sistema de logging del proyecto para mostrar información detallada del proceso.

## Troubleshooting

### Error: "No se encontró el episodio número X"
- Verifica que el número de episodio existe en el RSS
- Comprueba que el RSS esté accesible

### Error: "No se pudieron unificar los datos con WordPress"
- Los datos del RSS se utilizan como fallback
- Verifica la configuración de WordPress en `config.ini`

### Error: "No se encontraron episodios que coincidan con la búsqueda"
- Revisa el término de búsqueda
- Verifica el tipo de búsqueda seleccionado 