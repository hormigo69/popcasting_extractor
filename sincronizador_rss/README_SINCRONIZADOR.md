# Sincronizador RSS - Popcasting

Este sincronizador lee el feed RSS de Popcasting, enriquece los datos con información de WordPress y los guarda en Supabase.

## 🚀 Características

- **Lectura de RSS**: Descarga y procesa el feed RSS de Popcasting
- **Enriquecimiento con WordPress**: Busca información adicional en la API de WordPress
- **Almacenamiento en Supabase**: Guarda los episodios y canciones en la base de datos
- **Detección inteligente**: Compara por número de episodio para evitar duplicados
- **Logging detallado**: Registra todo el proceso de sincronización
- **Manejo de errores**: Gestiona errores de forma robusta

## 📋 Requisitos

- Python 3.8+
- Acceso a Supabase
- Acceso a la API de WordPress de Popcasting

## 🔧 Configuración

### 1. Variables de Entorno

Crea un archivo `.env` en el directorio raíz del proyecto con las siguientes variables:

```env
# Supabase
supabase_project_url=https://tu-proyecto.supabase.co
supabase_api_key=tu-api-key-de-supabase

# WordPress (opcional, para enriquecimiento de datos)
wordpress_url=https://popcasting.es
```

### 2. Configuración del RSS

Crea un archivo `config.ini` en el directorio `sincronizador_rss`:

```ini
[rss]
url = https://popcasting.es/feed/podcast/

[wordpress]
url = https://popcasting.es
```

## 🏗️ Arquitectura

El sincronizador está compuesto por los siguientes componentes:

### Componentes Principales

- **`ConfigManager`**: Gestiona la configuración y credenciales
- **`DatabaseManager`**: Maneja la conexión y operaciones con Supabase
- **`RSSDataProcessor`**: Procesa el feed RSS
- **`WordPressClient`**: Cliente para la API de WordPress
- **`WordPressDataProcessor`**: Procesa datos de WordPress
- **`DataProcessor`**: Orquestador que unifica todos los datos

### Flujo de Datos

1. **Lectura RSS**: Se descarga y procesa el feed RSS
2. **Detección de Episodios Nuevos**: Se compara por número de episodio con la BD
3. **Enriquecimiento WordPress**: Se buscan datos adicionales en WordPress
4. **Unificación**: Se combinan los datos del RSS y WordPress
5. **Almacenamiento**: Se guardan en Supabase (podcast + canciones)

## 🚀 Uso

### Ejecución Principal

```bash
cd sincronizador_rss/src
python main.py
```

### Ejecución de Pruebas

```bash
cd sincronizador_rss
python test_main.py
```

### Ejecución desde el Directorio Raíz

```bash
python sincronizador_rss/src/main.py
```

## 📊 Estructura de Datos

### Tabla `podcasts`

- `id`: ID único del podcast
- `guid`: GUID único del episodio (desde RSS)
- `title`: Título del episodio
- `date`: Fecha de publicación
- `url`: URL del episodio
- `download_url`: URL de descarga del audio
- `file_size`: Tamaño del archivo de audio
- `duration`: Duración en segundos
- `rss_playlist`: Playlist extraída del RSS
- `image_url`: URL de la imagen del episodio
- `program_number`: Número de programa
- `comments`: Comentarios adicionales
- `wordpress_id`: ID del post en WordPress
- `wordpress_title`: Título en WordPress
- `wordpress_content`: Contenido completo del post
- `wordpress_excerpt`: Extracto del post
- `wordpress_slug`: Slug del post
- `wordpress_date`: Fecha en WordPress
- `wordpress_modified`: Fecha de modificación
- `featured_image_url`: URL de la imagen destacada
- `wordpress_author`: Autor del post
- `wordpress_status`: Estado del post
- `wordpress_link`: Enlace al post
- `wordpress_categories`: Categorías del post
- `wordpress_tags`: Tags del post
- `web_playlist`: Playlist extraída del web (JSON)
- `web_songs_count`: Número de canciones del web
- `web_extra_links`: Enlaces adicionales
- `last_web_check`: Última verificación del web
- `created_at`: Fecha de creación en BD
- `updated_at`: Fecha de última actualización

### Tabla `songs`

- `id`: ID único de la canción
- `podcast_id`: ID del podcast al que pertenece
- `title`: Título de la canción
- `artist`: Artista
- `album`: Álbum
- `duration`: Duración en segundos
- `url`: URL de la canción (si está disponible)

## 📝 Logs

Los logs se guardan en:
- **Consola**: Salida en tiempo real
- **Archivo**: `sincronizador_rss/logs/sincronizador_rss.log`

### Niveles de Log

- **INFO**: Información general del proceso
- **DEBUG**: Información detallada para debugging
- **WARNING**: Advertencias (no críticas)
- **ERROR**: Errores que requieren atención

## 🔍 Monitoreo

El sincronizador proporciona un reporte final con:

- Total de episodios en el RSS
- Episodios nuevos encontrados
- Episodios procesados exitosamente
- Episodios con errores

## 🛠️ Desarrollo

### Estructura de Archivos

```
sincronizador_rss/
├── src/
│   ├── components/
│   │   ├── config_manager.py
│   │   ├── database_manager.py
│   │   ├── rss_data_processor.py
│   │   ├── wordpress_client.py
│   │   ├── wordpress_data_processor.py
│   │   └── data_processor.py
│   ├── utils/
│   │   └── logger.py
│   └── main.py
├── logs/
├── config.ini
├── test_main.py
└── README_SINCRONIZADOR.md
```

### Añadir Nuevos Componentes

1. Crear el archivo en `src/components/`
2. Implementar la funcionalidad
3. Importar en `main.py`
4. Inicializar en la función `main()`

### Modificar el Procesamiento

- **RSS**: Modificar `RSSDataProcessor`
- **WordPress**: Modificar `WordPressDataProcessor` o `WordPressClient`
- **Base de Datos**: Modificar `DatabaseManager`
- **Unificación**: Modificar `DataProcessor`

## 🐛 Solución de Problemas

### Error de Conexión a Supabase

1. Verificar las credenciales en `.env`
2. Comprobar la conectividad de red
3. Verificar que el proyecto de Supabase esté activo

### Error de Conexión a WordPress

1. Verificar la URL de WordPress en `config.ini`
2. Comprobar que la API esté disponible
3. Verificar la conectividad de red

### Episodios No Procesados

1. Revisar los logs para errores específicos
2. Verificar que el RSS contenga datos válidos
3. Comprobar que los números de programa se extraigan correctamente

### Episodios No Encontrados

1. Verificar que el número de programa se extraiga correctamente
2. Comprobar que la comparación por número de episodio funcione
3. Revisar que el episodio más reciente en BD sea correcto

## 📈 Mejoras Futuras

- [ ] Procesamiento en lotes para mejor rendimiento
- [ ] Reintentos automáticos en caso de error
- [ ] Notificaciones por email/Slack
- [ ] Dashboard web para monitoreo
- [ ] Sincronización incremental
- [ ] Backup automático antes de sincronizar
- [ ] Validación de datos antes de insertar
- [ ] Métricas de rendimiento

## 📄 Licencia

Este proyecto es parte del sistema de extracción de datos de Popcasting. 