# Arquitectura del Sistema

## 🏗️ Diseño General

El sincronizador RSS está diseñado con una arquitectura modular que separa responsabilidades y permite fácil mantenimiento y extensión. La arquitectura sigue el principio de **responsabilidad única** donde cada componente se encarga de una fuente de datos específica.

## 📦 Componentes Principales

### 1. ConfigManager (`src/components/config_manager.py`)
**Responsabilidad**: Gestión de configuración y credenciales

- Carga configuración desde `config.ini`
- Gestiona variables de entorno desde `.env`
- Proporciona credenciales de Supabase
- Configuración de RSS y WordPress

**Interfaces principales:**
```python
def get_supabase_credentials() -> dict
def get_rss_url() -> str
def get_wordpress_config() -> dict
```

### 2. RSSReader (`src/components/rss_reader.py`)
**Responsabilidad**: Lectura y descarga de feeds RSS

- Descarga feeds RSS usando `feedparser`
- Manejo de errores de conexión
- Validación de formato RSS
- Logging de información del feed

**Interfaces principales:**
```python
def __init__(self, feed_url: str)
def fetch_entries() -> list
```

### 3. RSSDataProcessor (`src/components/rss_data_processor.py`)
**Responsabilidad**: Procesamiento específico de datos RSS

- Extrae y procesa entradas del RSS
- Convierte formatos de fecha y duración
- Extrae números de programa y comentarios
- Prepara datos para la base de datos

**Interfaces principales:**
```python
def __init__(self, feed_url: str)
def fetch_and_process_entries() -> List[Dict]
def get_episode_by_title(title: str) -> Optional[Dict]
```

### 4. WordPressClient (`src/components/wordpress_client.py`)
**Responsabilidad**: Cliente para extracción de datos de WordPress

- Extrae datos de posts de WordPress
- Soporta extracción HTML (cuando la API REST no está disponible)
- Extrae playlists, imágenes y enlaces
- Manejo robusto de errores de conexión

**Interfaces principales:**
```python
def __init__(self, api_url: str)
def get_post_details_by_slug(slug: str) -> dict | None
def get_post_details_by_date_and_number(date: str, chapter_number: str) -> dict | None
```

### 5. WordPressDataProcessor (`src/components/wordpress_data_processor.py`)
**Responsabilidad**: Procesamiento específico de datos de WordPress

- Procesa datos de la API REST y extracción HTML
- Extrae categorías, etiquetas y metadatos
- Valida datos de WordPress
- Extrae slugs de URLs

**Interfaces principales:**
```python
def __init__(self)
def process_post_data(wordpress_data: Dict) -> Dict
def extract_slug_from_url(url: str) -> str
def validate_post_data(wordpress_data: Dict) -> bool
```

### 6. DataProcessor (`src/components/data_processor.py`)
**Responsabilidad**: Orquestador que unifica datos de múltiples fuentes

- Coordina los procesadores específicos
- Unifica datos del RSS y WordPress
- Proporciona interfaz de alto nivel
- Maneja casos donde algunas fuentes no están disponibles

**Interfaces principales:**
```python
def __init__(self, rss_processor: RSSDataProcessor, wordpress_processor: WordPressDataProcessor)
def process_entry(rss_entry, wordpress_data: Optional[Dict] = None) -> Dict
def get_unified_episodes(wordpress_client, limit: Optional[int] = None) -> List[Dict]
```

### 7. DatabaseManager (`src/components/database_manager.py`)
**Responsabilidad**: Interacción con Supabase

- Conexión a Supabase usando la API oficial
- Operaciones CRUD en la base de datos
- Detección del episodio más reciente por número de programa
- Inserción transaccional de podcasts y canciones
- Procesamiento y validación de datos JSON
- Manejo de errores de conexión
- Context manager para gestión de recursos

**Interfaces principales:**
```python
def __init__(self, supabase_url: str, supabase_key: str)
def get_latest_podcast() -> dict | None
def insert_full_podcast(podcast_data: dict)
def podcast_exists(guid: str) -> bool
def test_connection() -> bool
def close()
```

### 8. Logger (`src/utils/logger.py`)
**Responsabilidad**: Sistema de logging centralizado

- Logging a consola y archivo
- Niveles de log configurables
- Formato consistente de mensajes
- Rotación automática de logs

## 🔄 Flujo de Datos

```
1. ConfigManager
   ↓ (carga configuración)
2. RSSDataProcessor + WordPressDataProcessor
   ↓ (procesadores específicos)
3. DataProcessor (Orquestador)
   ↓ (unifica datos)
4. WordPressClient
   ↓ (extrae datos adicionales)
5. DatabaseManager
   ↓ (guarda en Supabase)
```

### Flujo Detallado de Unificación

```
RSS Feed → RSSDataProcessor → Datos RSS procesados
                                    ↓
WordPress → WordPressClient → WordPressDataProcessor → Datos WordPress procesados
                                    ↓
                            DataProcessor (Orquestador)
                                    ↓
                            Datos unificados completos
                                    ↓
                            DatabaseManager → Supabase (con detección de episodios nuevos)
```

## 🏛️ Principios de Arquitectura

### 1. Separación de Responsabilidades
- **RSSDataProcessor**: Solo procesa datos RSS
- **WordPressDataProcessor**: Solo procesa datos WordPress
- **DataProcessor**: Solo orquesta y unifica
- **WordPressClient**: Solo extrae datos de WordPress

### 2. Modularidad
- Cada componente puede funcionar independientemente
- Fácil testing de componentes individuales
- Reutilización de componentes
- Extensibilidad sin modificar componentes existentes

### 3. Robustez
- Manejo de casos donde WordPress no está disponible
- Fallbacks para datos faltantes
- Validación de datos en cada nivel
- Logging detallado para debugging

## 🛡️ Gestión de Errores

### Estrategia de Manejo de Errores

1. **Validación de Configuración**
   - Verificación de archivos de configuración
   - Validación de variables de entorno requeridas
   - Mensajes de error descriptivos

2. **Procesamiento de Datos**
   - Validación de datos RSS antes del procesamiento
   - Manejo de fechas inválidas
   - Extracción robusta de números de programa
   - Fallbacks para datos faltantes

3. **Conexión a Fuentes Externas**
   - Reintentos automáticos en fallos de red
   - Timeouts configurables
   - Manejo de APIs no disponibles (WordPress REST API)
   - Extracción HTML como fallback

4. **Unificación de Datos**
   - Priorización de fuentes de datos
   - Manejo de conflictos entre fuentes
   - Validación de datos unificados
   - Logging de decisiones de unificación

## 🔧 Configuración

### Archivos de Configuración

1. **config.ini**: Configuración del sistema
   ```ini
   [database]
   use_env_vars = true
   
   [rss]
   url = https://feeds.feedburner.com/Popcasting
   
   [wordpress]
   url = https://popcastingpop.com
   ```

2. **.env**: Credenciales sensibles
   ```env
   supabase_project_url=https://proyecto.supabase.co
   supabase_api_key=api-key-secreta
   ```

## 📊 Logging y Monitoreo

### Estructura de Logs

- **Ubicación**: `logs/sincronizador_rss.log`
- **Formato**: `YYYY-MM-DD HH:MM:SS - module - LEVEL - message`
- **Niveles**: DEBUG, INFO, WARNING, ERROR, CRITICAL

### Información Registrada

- Inicio/fin de operaciones de cada componente
- Errores de conexión y procesamiento
- Métricas de extracción (canciones encontradas, imágenes, etc.)
- Decisiones de unificación de datos
- Cambios de configuración

## 🔄 Extensibilidad

### Puntos de Extensión

1. **Nuevos Procesadores de Datos**
   - Implementar interfaces estándar
   - Configuración vía config.ini
   - Logging integrado
   - Integración con el orquestador

2. **Nuevas Fuentes de Datos**
   - RSS, APIs REST, archivos locales
   - Adaptadores configurables
   - Validación de esquemas
   - Procesadores específicos por fuente

3. **Nuevos Destinos**
   - Bases de datos adicionales
   - APIs externas
   - Sistemas de archivos
   - Integración con el DatabaseManager

### Patrón de Extensión

```python
# Nuevo procesador de datos
class NewDataProcessor:
    def __init__(self, config):
        pass
    
    def process_data(self, raw_data):
        pass
    
    def validate_data(self, data):
        pass

# Integración con orquestador
class DataProcessor:
    def __init__(self, rss_processor, wordpress_processor, new_processor):
        self.new_processor = new_processor
```

## 🚀 Optimizaciones Implementadas

### Rendimiento

- Procesamiento específico por fuente de datos
- Extracción paralela de datos RSS y WordPress
- Caché de configuración en ConfigManager
- Logging eficiente con niveles apropiados

### Escalabilidad

- Arquitectura modular permite escalado horizontal
- Procesadores independientes pueden ejecutarse en paralelo
- Orquestador centralizado para coordinación
- Interfaces estándar para nuevos componentes

## 🔒 Seguridad

### Gestión de Credenciales

- Variables de entorno para secretos
- No hardcoding de credenciales
- ConfigManager centraliza gestión de credenciales
- Auditoría de acceso vía logging

### Validación de Datos

- Sanitización de inputs en cada procesador
- Validación de esquemas de datos
- Prevención de inyección en consultas
- Rate limiting en WordPressClient

## 📈 Métricas y Monitoreo

### Métricas de Procesamiento

- Número de episodios procesados por fuente
- Tasa de éxito en extracción de datos
- Tiempo de procesamiento por componente
- Calidad de datos unificados

### Indicadores de Salud

- Disponibilidad de fuentes de datos
- Errores de conexión y procesamiento
- Tiempo de respuesta de APIs externas
- Uso de recursos del sistema 