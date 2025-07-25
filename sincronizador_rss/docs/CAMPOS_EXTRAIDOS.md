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

### Campos por Entrada (API REST)
- **id**: ID numérico del post ✅
- **title.rendered**: Título del post ✅
- **content.rendered**: Contenido completo del post ✅
- **excerpt.rendered**: Extracto del post ✅
- **slug**: Slug del post ✅
- **date**: Fecha de publicación ✅
- **modified**: Fecha de modificación ✅
- **jetpack_featured_media_url**: URL de imagen destacada ✅
- **author**: ID del autor ✅
- **status**: Estado del post ✅
- **link**: URL del post ✅
- **_embedded.wp:term**: Categorías y etiquetas ✅

### Campos por Entrada (Extracción HTML)
- **title**: Título del post ✅
- **wordpress_url**: URL del post ✅
- **cover_image_url**: URL de la imagen de portada ✅
- **web_extra_links**: Enlaces adicionales del post ✅
- **web_playlist**: Playlist extraída del contenido ✅
- **content_length**: Tamaño del contenido en bytes ✅
- **date**: Fecha de publicación ✅

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

## 🔄 Datos Unificados (DataProcessor - Orquestador)

### Estructura de Datos Unificados

Los datos unificados combinan información del RSS y WordPress en una estructura coherente:

#### Campos Base (RSS)
- **guid**: ID único del episodio
- **title**: Título del episodio
- **link**: URL del episodio
- **published_date**: Fecha de publicación
- **summary**: Resumen/playlist del RSS
- **download_url**: URL de descarga del MP3
- **file_size**: Tamaño del archivo
- **duration**: Duración en segundos
- **image_url**: URL de imagen del RSS
- **program_number**: Número del programa
- **comments**: Comentarios extraídos del título

#### Campos WordPress (cuando están disponibles)
- **wordpress_id**: ID numérico del post
- **wordpress_title**: Título del post
- **wordpress_content**: Contenido completo
- **wordpress_excerpt**: Extracto del post
- **wordpress_slug**: Slug del post
- **wordpress_date**: Fecha del post
- **wordpress_modified**: Fecha de modificación
- **featured_image_url**: URL de imagen destacada
- **wordpress_author**: ID del autor
- **wordpress_status**: Estado del post
- **wordpress_link**: URL del post
- **wordpress_categories**: Lista de categorías
- **wordpress_tags**: Lista de etiquetas
- **wordpress_playlist_data**: Datos de playlist procesados
- **web_extra_links**: Enlaces adicionales
- **content_length**: Tamaño del contenido

### Priorización de Datos

1. **Imágenes**: WordPress tiene prioridad sobre RSS
2. **Playlists**: Se combinan datos de ambas fuentes
3. **Metadatos**: WordPress complementa datos del RSS
4. **Fechas**: Se usa la fecha del RSS como principal

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
- [x] ✅ Procesador WordPress implementado (`WordPressDataProcessor`)
- [x] ✅ Orquestador de datos implementado (`DataProcessor`)
- [x] ✅ Unificación de datos RSS + WordPress funcionando
- [x] ✅ Extracción de fechas reales del RSS para búsqueda en WordPress
- [x] ✅ Sistema de logging integrado
- [x] ✅ Integración con base de datos implementada (`DatabaseManager`)
- [x] ✅ Sistema de sincronización automática implementado
- [x] ✅ Detección inteligente de episodios nuevos por número de programa
- [x] ✅ Procesamiento correcto de JSON de playlists
- [x] ✅ Cálculo preciso de número de canciones
- [ ] Implementar extracción de metadatos MP3
- [ ] Añadir validación de datos unificados

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
  - `get_post_details_by_slug()`: Busca post por slug (API REST)
  - `_extract_cover_image()`: Extrae imagen de portada
  - `_extract_extra_links()`: Extrae enlaces adicionales (filtra Ko-fi)
  - `_extract_playlist()`: Extrae playlist de canciones
- **Características**:
  - Compatible con episodios antiguos y modernos
  - Filtrado inteligente de URLs y texto no musical
  - Búsqueda en cascada: párrafos centrados → listas → párrafos generales
  - Formato JSON para playlist y enlaces
  - Soporte para API REST y extracción HTML

### WordPressDataProcessor
- **Archivo**: `sincronizador_rss/src/components/wordpress_data_processor.py`
- **Función**: Procesa datos de WordPress (API REST y HTML)
- **Métodos principales**:
  - `process_post_data()`: Procesa datos del post
  - `extract_slug_from_url()`: Extrae slug de URLs
  - `validate_post_data()`: Valida datos del post
- **Características**:
  - Detecta automáticamente formato de datos (API vs HTML)
  - Extrae categorías y etiquetas
  - Procesa datos de playlist
  - Validación robusta de datos

### DataProcessor (Orquestador)
- **Archivo**: `sincronizador_rss/src/components/data_processor.py`
- **Función**: Unifica datos del RSS y WordPress
- **Métodos principales**:
  - `process_entry()`: Procesa entrada individual
  - `get_unified_episodes()`: Obtiene episodios unificados
  - `process_single_episode()`: Procesa episodio individual con WordPress
  - `_unify_rss_with_wordpress()`: Unifica datos usando número de programa
- **Características**:
  - Orquestador principal del sistema
  - Coordina procesadores específicos
  - Maneja casos donde WordPress no está disponible
  - Proporciona interfaz de alto nivel
  - Extrae fechas reales del RSS para búsqueda en WordPress

### DatabaseManager
- **Archivo**: `sincronizador_rss/src/components/database_manager.py`
- **Función**: Gestiona conexión y operaciones con Supabase
- **Métodos principales**:
  - `get_latest_podcast()`: Obtiene el episodio más reciente por número de programa
  - `insert_full_podcast()`: Inserta podcast completo con canciones
  - `podcast_exists()`: Verifica existencia de episodio por GUID
  - `get_table_info()`: Obtiene información de estructura de tablas
- **Características**:
  - Conexión segura a Supabase
  - Inserción transaccional de datos
  - Procesamiento automático de JSON de playlists
  - Cálculo preciso de número de canciones
  - Mapeo correcto de campos entre procesador y BD 