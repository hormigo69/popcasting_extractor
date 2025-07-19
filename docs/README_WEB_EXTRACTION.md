# Extracción de Información Web de Popcasting

Esta feature permite extraer información adicional de la web de Popcasting para complementar los datos del RSS y detectar discrepancias.

## Funcionalidades

### 🎯 Objetivos Principales

1. **Extraer URLs de WordPress** de cada episodio
2. **Obtener imágenes de portada** de los episodios
3. **Verificar playlists** comparando RSS vs Web
4. **Detectar enlaces extras** en las páginas web
5. **Identificar discrepancias** entre fuentes de datos

### 📊 Información Extraída

- **URL de WordPress**: Enlace directo a la página del episodio
- **Imagen de portada**: URL de la imagen destacada del episodio
- **Playlist de la web**: Lista de canciones extraída de la página
- **Enlaces extras**: Enlaces adicionales encontrados en la web
- **Fecha de verificación**: Cuándo se realizó la última extracción

## Uso

### Scripts Principales

#### 1. Extracción Individual
```bash
# Extraer información de un episodio específico
python web_extractor.py extract --episode-id 1

# Ver información de un episodio
python web_extractor.py info 1

# Comparar RSS vs Web
python web_extractor.py compare 1
```

#### 2. Procesamiento Automático
```bash
# Procesar múltiples episodios automáticamente
python batch_web_extraction.py --max-episodes 10 --delay 2

# Listar episodios sin información web
python web_extractor.py list --limit 20
```

#### 3. Generación de Reportes
```bash
# Reporte detallado de discrepancias
python web_report.py --max-episodes 50

# Reporte simple de lista
python web_report.py --type list --max-episodes 20

# Guardar reporte con nombre específico
python web_report.py --output mi_reporte.json
```

### Comandos del CLI

```bash
# Ayuda general
python web_extractor.py --help

# Comandos disponibles
python web_extractor.py extract --help
python web_extractor.py compare --help
python web_extractor.py list --help
python web_extractor.py info --help
```

## Estructura de la Base de Datos

### Nuevos Campos Añadidos

```sql
ALTER TABLE podcasts ADD COLUMN wordpress_url TEXT;
ALTER TABLE podcasts ADD COLUMN cover_image_url TEXT;
ALTER TABLE podcasts ADD COLUMN web_extra_links TEXT;
ALTER TABLE podcasts ADD COLUMN web_playlist TEXT;
ALTER TABLE podcasts ADD COLUMN last_web_check TEXT;
```

### Funciones de Base de Datos

- `update_web_info()`: Actualiza información web de un episodio
- `get_podcasts_without_web_info()`: Obtiene episodios sin información web
- `get_podcast_web_info()`: Obtiene información web de un episodio

## Arquitectura

### Servicios Principales

#### `WebExtractor`
- **Responsabilidad**: Extraer información de páginas web
- **Métodos principales**:
  - `extract_all_web_info()`: Procesa múltiples episodios
  - `_find_wordpress_url()`: Busca URL de WordPress
  - `_extract_episode_page_info()`: Extrae datos de la página
  - `compare_rss_vs_web()`: Compara fuentes de datos

#### `WebReportGenerator`
- **Responsabilidad**: Generar reportes de análisis
- **Métodos principales**:
  - `generate_discrepancy_report()`: Reporte detallado
  - `generate_episode_list_report()`: Reporte simple
  - `print_summary()`: Mostrar resumen en consola

### Algoritmos de Extracción

#### 1. Búsqueda de URLs de WordPress
```python
# Patrones de URL probados
possible_urls = [
    f"{base_url}/{date.replace('-', '/')}/popcasting-{program_number}/",
    f"{base_url}/{date[:4]}/{date[5:7]}/{date[8:10]}/popcasting-{program_number}/",
    f"{base_url}/popcasting-{program_number}/",
]
```

#### 2. Extracción de Playlists
```python
# Patrones de canciones reconocidos
patterns = [
    r'^(.+?)\s*[-–—]\s*(.+)$',  # Artista - Título
    r'^(.+?)\s*:\s*(.+)$',      # Artista: Título
    r'^(.+?)\s*·\s*(.+)$',      # Artista · Título (Popcasting)
]
```

#### 3. Detección de Enlaces Extras
- Busca enlaces con estilo específico (`#ff99cc`)
- Filtra enlaces de navegación
- Evita duplicados

## Resultados y Estadísticas

### Ejemplo de Reporte

```
📊 REPORTE DE DISCREPANCIAS RSS vs WEB
============================================================
📄 Episodios analizados: 5
✅ Sin discrepancias: 0
⚠️  Con discrepancias: 5
📈 Tasa de discrepancias: 100.0%

🎵 Discrepancias en canciones:
   Total: 27
   Promedio por episodio: 5.4
   Episodios afectados: 5
```

### Tipos de Discrepancias Detectadas

1. **Diferente número de canciones**: RSS vs Web
2. **Diferencias en títulos**: Títulos completos vs abreviados
3. **Diferencias en artistas**: Nombres ligeramente diferentes
4. **Enlaces extras**: Enlaces solo en RSS o solo en Web

## Configuración y Optimización

### Delays y Rate Limiting
```python
# Delay entre requests para ser respetuoso con el servidor
extractor.delay_between_requests = 2.0  # segundos
```

### Headers de Usuario
```python
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}
```

## Archivos de Salida

### Reportes JSON
- Ubicación: `outputs/web_discrepancy_report_YYYYMMDD_HHMMSS.json`
- Contenido: Análisis completo de discrepancias
- Formato: JSON estructurado con metadatos

### Logs
- Errores de parsing: `logs/parsing_errors.log`
- Estadísticas: `logs/extraction_stats.log`

## Casos de Uso

### 1. Verificación de Calidad de Datos
```bash
# Extraer información de episodios recientes
python batch_web_extraction.py --max-episodes 20

# Generar reporte de calidad
python web_report.py --max-episodes 20
```

### 2. Detección de Errores
```bash
# Comparar episodio específico
python web_extractor.py compare 1

# Ver detalles completos
python web_extractor.py info 1
```

### 3. Procesamiento Masivo
```bash
# Procesar todos los episodios disponibles
python batch_web_extraction.py --max-episodes 1000 --delay 3

# Generar reporte completo
python web_report.py --max-episodes 1000
```

## Limitaciones y Consideraciones

### Limitaciones Técnicas
- Dependencia de la estructura HTML de WordPress
- Posibles cambios en la estructura de la web
- Rate limiting del servidor web

### Consideraciones Éticas
- Respeto por el servidor web (delays entre requests)
- Uso responsable de recursos
- Cumplimiento de robots.txt

### Mantenimiento
- Monitoreo de cambios en la estructura web
- Actualización de patrones de extracción
- Verificación periódica de funcionalidad

## Próximas Mejoras

1. **Detección automática de cambios** en la estructura web
2. **Extracción de metadatos adicionales** (duración, categorías)
3. **Interfaz web** para visualizar discrepancias
4. **Notificaciones automáticas** de errores críticos
5. **Integración con APIs** de música (Spotify, Discogs) 