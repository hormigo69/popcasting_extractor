
[x] leer los links de los episodios del feed de popcasting
    ✅ Implementado en rama feature/episode-links
    ✅ Extrae URLs web y de descarga de iVoox
    ✅ Almacena tamaños de archivo
    ✅ 100% de episodios con links completos


[x] leer los links extras de los episodios del feed de popcasting. están al final del campo <description>, normalmente separados por un número no definido de ::::  pero no siempre. a veces hay una / o similar. Ejemplo: :::::: weird herald https://weirdherald.bandcamp.com/album/just-yesterday :::::: yo no quería ser miqui puig https://miquipuig.com/author/miqui-admin-puig-web/ :::::: invita a Popcasting a café https://ko-fi.com/popcasting ]]>
    ✅ Implementado en rama feature/extra-episode-links
    ✅ Extrae links extras con texto descriptivo
    ✅ Almacena en nueva tabla extra_links
    ✅ 333 links extras extraídos de 144 episodios (36.5%)
    ✅ Detecta y limpia datos contaminados cuando las descripciones se mezclan con canciones
    ✅ Corrige asignaciones incorrectas de enlaces extras



[x] Control de cambios para no reescribir la base de datos si no hay cambios.
    ✅ Implementado en rama feature/change-detection
    ✅ Detecta cambios en canciones y enlaces extras
    ✅ Evita operaciones innecesarias
    ✅ Mejora rendimiento y eficiencia
    ✅ 95.8% de reducción en operaciones de base de datos


[x] Extraer información de la web de cada episodio. 
    ✅ Implementado en rama feature/web-episode-extraction
    ✅ Extrae URLs de WordPress de cada episodio
    ✅ Obtiene imágenes de portada de los episodios
    ✅ Verifica playlists comparando RSS vs Web
    ✅ Detecta enlaces extras en las páginas web
    ✅ Identifica discrepancias entre fuentes de datos
    ✅ Sistema de reportes automáticos de discrepancias
    ✅ Procesamiento masivo de episodios
    ✅ CLI completo para gestión de extracción web
    ✅ Documentación completa en docs/README_WEB_EXTRACTION.md


[x] Montar la base de datos en supabase. La idea es usar supabase como base de datos en lugar de sqlite.
    ✅ Implementado en rama feature/supabase-migration
    ✅ Migración completa de SQLite a Supabase (PostgreSQL)
    ✅ Sistema híbrido que puede alternar entre SQLite y Supabase
    ✅ 396 podcasts, 6,353 canciones y 240 links extras migrados
    ✅ Configuración automática mediante variable DATABASE_TYPE
    ✅ Scripts de migración y pruebas completos
    ✅ Documentación completa en migration/README.md
    ✅ Resumen de migración en SUPABASE_MIGRATION_SUMMARY.md
    ✅ Sistema de configuración dinámico en services/config.py
    ✅ Servicio completo de Supabase en services/supabase_database.py
    ✅ Pruebas de conexión y CRUD exitosas
    ✅ Integración completa con el programa principal


## Próximos pasos:

[ ] Crear el front del buscador de canciones
    - Interfaz web para buscar canciones por artista, título, episodio
    - Filtros avanzados por fecha, género, etc.
    - Integración con Supabase para consultas en tiempo real

[ ] Extraer información extra de las canciones de las api de spotify, Discogs, etc.
    - Integración con APIs de música para enriquecer datos
    - Información de álbumes, géneros, años de lanzamiento
    - Imágenes de portada de álbumes
    - Datos de popularidad y reviews

[ ] Transcribir los episodios de popcasting
    - Sistema de transcripción automática de audio
    - Almacenamiento de transcripciones en base de datos
    - Búsqueda de texto en transcripciones

[ ] Añadir el comentario de cada canción de la transcripción a la tabla de canciones
    - Extraer comentarios específicos de cada canción
    - Vincular comentarios con canciones en la base de datos
    - Sistema de búsqueda por comentarios

[ ] Crear un cms que añada los campos y cree el RSS desde ahí en lugar de al revés
    - Interfaz de administración para gestionar episodios
    - Editor de playlists y metadatos
    - Generación automática de RSS feeds
    - Sistema de usuarios y permisos

[ ] Optimizaciones y mejoras técnicas
    - Cache de consultas frecuentes
    - Optimización de índices en Supabase
    - Sistema de backup automático
    - Monitoreo y alertas de rendimiento