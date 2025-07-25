# Campos Extraídos - Sincronizador RSS

Este documento describe todos los campos que extraemos de las diferentes fuentes de datos para el sincronizador RSS de Popcasting.

## 📡 Fuente: RSS Feed (iVoox)

### Información del Feed
- **title**: Título del podcast (ej: "Popcasting")
- **description**: Descripción del podcast
- **language**: Idioma del feed (ej: "es")
- **generator**: Generador del feed (ej: "iVoox")

### Campos por Entrada/Episodio

#### Información Básica
- **title**: Título del episodio (ej: "Popcasting485")
- **link**: URL del episodio en iVoox
- **id**: ID único del episodio (ej: "https://www.ivoox.com/153710543")
- **guid**: Identificador único (mismo que id)

#### Fechas
- **published**: Fecha de publicación (formato: "Thu, 24 Jul 2025 10:49:36 +0200")
- **published_parsed**: Fecha parseada como struct_time

#### Contenido
- **summary**: Resumen del episodio (lista de canciones)
- **description**: Descripción completa (mismo que summary)
- **subtitle**: Subtítulo del episodio
- **content**: Contenido completo del episodio

#### Metadatos de Audio
- **itunes_duration**: Duración del episodio (ej: "01:51:12")
- **itunes_episodetype**: Tipo de episodio (ej: "full")
- **itunes_explicit**: Contenido explícito (generalmente None)

#### Archivos de Audio
- **enclosures**: Lista de archivos adjuntos
  - **type**: Tipo MIME (ej: "audio/mpeg")
  - **href**: URL directa del archivo MP3
  - **length**: Tamaño del archivo en bytes

#### Imágenes
- **image**: Imagen del episodio
  - **href**: URL de la imagen

#### Detalles Adicionales
- **title_detail**: Detalles del título (tipo, idioma, base, valor)
- **summary_detail**: Detalles del resumen
- **subtitle_detail**: Detalles del subtítulo
- **links**: Lista de enlaces relacionados
- **guidislink**: Indica si el GUID es un enlace

---

## 🌐 Fuente: WordPress (Implementado ✅)

### Campos por Entrada
- **Título**: Título del post ✅
- **Contenido**: Contenido completo del post ✅
- **Fecha de publicación**: Fecha de publicación ✅
- **URL**: URL del post ✅
- **Imagen destacada**: URL de la imagen destacada ✅
- **Lista de canciones**: Playlist extraída del contenido ✅
- **Enlaces adicionales**: Enlaces extras del post ✅

---

## 🎵 Fuente: Archivos MP3 (Pendiente)

### Metadatos de Audio
- **Título**: Título del archivo
- **Artista**: Artista principal
- **Álbum**: Nombre del álbum
- **Año**: Año de lanzamiento
- **Género**: Género musical
- **Duración**: Duración en segundos
- **Bitrate**: Calidad del audio
- **Tamaño**: Tamaño del archivo
- **Formato**: Formato del archivo (MP3, etc.)

### Metadatos Específicos
- **Comentarios**: Comentarios adicionales
- **Letra**: Letra de la canción (si está disponible)
- **Composer**: Compositor
- **Track Number**: Número de pista
- **Disc Number**: Número de disco

---

## 📊 Base de Datos (Supabase - Estructura Real)

### Tabla: `podcasts`

| Campo | Tipo | Descripción | Ejemplo | De dónde viene
|-------|------|-------------|---------|-----------------|
| `id` | integer | ID único del episodio | 233 | generado por la base de datos
| `title` | text | Título del episodio | "Popcasting253" | extraído del RSS
| `date` | text | Fecha del episodio | "2015-12-31" | extraído del RSS
| `url` | text | URL del episodio en iVoox | "https://www.ivoox.com/popcasting253..." | extraído del RSS
| `download_url` | text | URL directa del archivo MP3 | "https://www.ivoox.com/popcasting253_mf_..." | extraído del RSS
| `file_size` | integer | Tamaño del archivo en bytes | 69291363 | extraído del RSS
| `program_number` | integer | Número del programa | 253 | calculado desde title
| `wordpress_url` | text | URL del post en WordPress | "https://popcastingpop.com/2016/01/01/2059/" | extraído del WordPress
| `cover_image_url` | text | URL de la imagen de portada | "https://popcastingpop.com/wp-content/uploads/..." | extraído del WordPress
| `web_extra_links` | text | Enlaces adicionales del web | "[]" | extraído del WordPress
| `web_playlist` | text | Playlist extraída del web (JSON) | "[{\"position\": 1, \"artist\": \"jimmy whispers\"...}]" | extraído del WordPress
| `last_web_check` | text | Última verificación del web | "2025-07-21T17:58:06.587949+00:00" | generado por el sistema
| `created_at` | text | Fecha de creación en BD | "2025-07-19T15:47:20.363426+00:00" | generado por el sistema
| `updated_at` | text | Fecha de última actualización | "2025-07-25T08:06:18.883345+00:00" | generado por el sistema
| `web_songs_count` | integer | Número de canciones del web | 15 | calculado desde web_playlist
| `comments` | unknown | Comentarios (actualmente NULL) | None | calculado desde title
| `duration` | integer | Duración en segundos | 4330 | extarido del extractor de mp3 / extraído del RSS
| `rss_playlist` | text | Playlist extraída del RSS (JSON) | "<![CDATA[ the international submarine band · blue eyes  ::... >" | extraído del RSS

### Tabla: `songs`

| Campo | Tipo | Descripción | Ejemplo |
|-------|------|-------------|---------|
| `id` | integer | ID único de la canción | 16277 |
| `title` | text | Título de la canción | "calling all angels" |
| `artist` | text | Artista de la canción | "jane siberry" |
| `position` | integer | Posición en el episodio | 10 |
| `podcast_id` | integer | ID del episodio (FK) | 79 |
| `created_at` | text | Fecha de creación | "2025-07-25T08:40:15.528647+00:00" |

---

## 🔄 Mapeo de Campos

### RSS → Base de Datos (Confirmado ✅)
- `title` → `podcasts.title` ✅
- `published` → `podcasts.date` ✅ (convertido a ISO)
- `link` → `podcasts.url` ✅
- `enclosures[0].href` → `podcasts.download_url` ✅
- `enclosures[0].length` → `podcasts.file_size` ✅
- `summary` → `podcasts.rss_playlist` ✅
- `itunes_duration` → `podcasts.duration` ✅ (convertido a segundos)
- `title` → `podcasts.program_number` ✅ (extraído con regex)
- `title` → `podcasts.comments` ✅ (extraído con regex)

### WordPress → Base de Datos (Confirmado ✅)
- `title` → `podcasts.title` ✅
- `content` → `podcasts.web_playlist` ✅ (extraído y parseado)
- `date` → `podcasts.date` ✅
- `link` → `podcasts.wordpress_url` ✅
- `featured_image` → `podcasts.cover_image_url` ✅
- `extra_links` → `podcasts.web_extra_links` ✅ (filtra Ko-fi)

### MP3 → Base de Datos
- `duration` → `podcasts.duration`
- `title` → `songs.title`
- `artist` → `songs.artist`
- `album` → (no se almacena actualmente)
- `year` → (no se almacena actualmente)

---

## 📝 Notas de Implementación

### Prioridades de Extracción
1. **RSS**: Fuente principal, siempre disponible
2. **WordPress**: Fuente secundaria, para contenido adicional
3. **MP3**: Metadatos de audio, para validación y enriquecimiento

### Campos Críticos
- **Título**: Siempre requerido
- **Fecha**: Para ordenamiento cronológico
- **URL de audio**: Para descarga
- **Playlist**: Contenido principal del episodio

### Campos Opcionales
- **Duración**: Puede calcularse desde el MP3
- **Imágenes**: Para enriquecimiento visual
- **Metadatos adicionales**: Para búsqueda y filtrado

### Relaciones de Base de Datos
- **podcasts.id** → **songs.podcast_id** (1:N)
- Un episodio puede tener múltiples canciones
- Las canciones siempre pertenecen a un episodio

---

## 🔧 Próximos Pasos

- [x] ✅ Estructura de base de datos documentada
- [x] ✅ Procesador RSS implementado (`RSSDataProcessor`)
- [x] ✅ Mapeo de campos RSS confirmado
- [x] ✅ Cliente WordPress implementado (`WordPressClient`)
- [x] ✅ Mapeo de campos WordPress confirmado
- [ ] Implementar extracción de metadatos MP3
- [ ] Implementar integración con base de datos
- [ ] Añadir validación de datos
- [ ] Crear sistema de logging de extracción

## 🛠️ Componentes Implementados

### RSSDataProcessor
- **Archivo**: `sincronizador_rss/src/components/rss_data_processor.py`
- **Función**: Procesa datos del RSS y los prepara para la BD
- **Métodos principales**:
  - `fetch_and_process_entries()`: Descarga y procesa todas las entradas
  - `get_episode_by_title()`: Busca episodio específico por título
- **Transformaciones**:
  - Fechas RSS → ISO format
  - Duración "HH:MM:SS" → segundos
  - Extracción de número de programa con regex
  - Extracción de comentarios con regex (sin paréntesis)
  - Validación y limpieza de datos

### WordPressClient
- **Archivo**: `sincronizador_rss/src/components/wordpress_client.py`
- **Función**: Extrae información de posts de WordPress
- **Métodos principales**:
  - `get_post_details_by_date_and_number()`: Busca post por fecha y número
  - `_extract_cover_image()`: Extrae imagen de portada
  - `_extract_extra_links()`: Extrae enlaces adicionales (filtra Ko-fi)
  - `_extract_playlist()`: Extrae playlist de canciones
- **Características**:
  - Compatible con episodios antiguos y modernos
  - Filtrado inteligente de URLs y texto no musical
  - Búsqueda en cascada: párrafos centrados → listas → párrafos generales
  - Formato JSON para playlist y enlaces 