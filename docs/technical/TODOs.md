
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
    ✅ **CORREGIDO**: Mejorado algoritmo de búsqueda de URLs para manejar discrepancias entre numeración RSS y web
    ✅ **CORREGIDO**: Extracción masiva exitosa con 91.7% de tasa de éxito (363/396 episodios)
    ✅ **CORREGIDO**: Script batch_web_extraction.py para procesamiento automático completo


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


[x] cargar la informaicón de los episodios antiguos. 
    Estos siguen una lógica diferente. No están en el RSS y en la web están varios en una página.
    Las páginas son:
        archivos del 00 al 20: https://popcastingpop.com/archivo-popcasting/
        archivos del 21 al 41: https://popcastingpop.com/archivo-popcasting-21-40/
        archivos del 42 al 63: https://popcastingpop.com/archivo-popcasting-42-62/
        archivos del 64 al 91: https://popcastingpop.com/programas-anteriores-64-91/

    La estructura del la informacióna  extraer es:
    - url de la web
    - url de la imagen de la portada - https://popcastingpop.com/wp-content/uploads/2009/09/patrick.jpg y https://popcastingpop.com/wp-content/uploads/2009/09/tyrone.jpg
    - lista de reproducción - <p style="text-align:center">the go-betweens · here comes a city :: ernest ranglin · surfin :: patrick wolf · the libertine :: vashti bunyan · i’d like to walk around in your mind :: husky rescue · new light of tomorrow :: mink deville · can’t do without it :: tyrone davies · can i change my mind :: madonna · gambler :: annie · my heartbeat</p>
    - enlaces extras - 
    - fecha - <span style="font-family:Trebuchet MS"><span style="font-size:12px">[15.5.2005]</span></span>
    - número de episodio - <span style="font-family:Trebuchet MS;color:#ccecff"><span style="font-size:14px">programa #0</span></span>
    - título
    - download_url - <audio class="wp-audio-shortcode" id="audio-151-1_html5" preload="none" style="width: 100%; height: 100%;" src="http://www.ivoox.com/popcasting000_md_1079313_1.mp3?_=1"><source type="audio/mpeg" src="http://www.ivoox.com/popcasting000_md_1079313_1.mp3?_=1"><a href="http://www.ivoox.com/popcasting000_md_1079313_1.mp3">http://www.ivoox.com/popcasting000_md_1079313_1.mp3</a></audio>
    

[x] optimizar los tipos de campo de la base de datos y asegurarnos de que el importador los guarda con el tipo de dato correcto.
    ✅ Implementado en scripts/utils/optimize_database_types.py
    ✅ Script SQL para Supabase en migration/optimize_supabase_schema.sql
    ✅ Esquemas actualizados en services/database.py y migration/supabase_schema.sql
    ✅ Funciones add_podcast_if_not_exists actualizadas con validación de tipos
    ✅ Campos optimizados en la tabla podcasts:
        - program_number: TEXT -> INTEGER
        - date: TEXT -> DATE
        - title: TEXT (mantener)
        - url: TEXT (mantener)
        - download_url: TEXT (mantener)
        - cover_image_url: TEXT (mantener)
    ✅ 91 fechas y 1 program_number optimizados en Supabase
    ✅ Validación automática de tipos en tiempo de inserción

[x] hacer script que haga  un backup de la base de datos supabase. scripts/backup_supabase_simple.py
    ✅ Implementado en scripts/backup_supabase_simple.py
    ✅ Script de backup simple para Supabase
    ✅ Exporta tablas a JSON y CSV con timestamp
    ✅ Directorio de backup en backups/
    ✅ Resumen de backup en resumen.txt
    ✅ Pruebas de conexión y backup exitosas

[x] Verificar la integridad de la Tabla podcasts en la BD

    ✅ Verificar que no faltan números de capítulos entre el 0 y el 484
    ✅ si ordenamos por número de capítulo, las fechas deberían de ser correlativas. Es decir, no hay fechas que no estén en orden
    ✅ marcamos qué campos faltan en qué filas. Habrá algunos que sea correcto que falten (links por ejemplo) pero otros no
    ✅ Script de verificación implementado en scripts/utils/verify_podcasts_integrity.py
    ✅ Compatible solo con Supabase
    ✅ Genera reportes detallados en pantalla y archivo
    ✅ Detecta 12 números de capítulo faltantes (#83, #92, #93, #97, #99, #100, #102, #103, #104, #105, #106, #148)
    ✅ Detecta problemas de secuencia de fechas (episodios duplicados con fechas diferentes)
    ✅ Detecta campos obligatorios faltantes
    ✅ Reporte completo con recomendaciones y estadísticas
    ✅ **CORREGIDO**: Eliminados 6 episodios duplicados automáticamente
    ✅ **CORREGIDO**: Arreglado program_number faltante en episodio #0
    ✅ **CORREGIDO**: Corregida fecha incorrecta del episodio #62 (2014 → 2008-01-01)
    ✅ **CORREGIDO**: Secuencia de fechas ahora perfecta (0 problemas)
           ✅ **CORREGIDO**: Todos los campos obligatorios presentes (0 faltantes)
       ✅ **COMPLETADO**: Colección de episodios completa (485/485 episodios)
       ✅ **CONSOLIDADO**: Script consolidate_manual_episodes.py para regeneración de BDD
       ✅ **ARCHIVO**: manual_episodes.json con todos los episodios manuales
       ✅ **LIMPIEZA**: Scripts auxiliares eliminados, solo quedan los esenciales
    ✅ verificar que las url de los capítulos y de los mp3 son coherentes. Esto es, que tienen una pinta similar, para asegurarnos de que no hemos cometido errores en el scrapping. Los formatos son:
        url - (enlace al episodio en ivoox) https://www.ivoox.com/popcasting482-audios-mp3_rf_151858068_1.html
        download_url - (enlace de descarga del mp3) https://www.ivoox.com/popcasting482_mf_151858068_feed_1.mp3
        wordpress_url - (el enlace al wordpress de popcasting) https://popcastingpop.com/2025/07/18/popcasting-484/
        cover_image_url (enlace a la imagen de cabecera del programa) https://popcastingpop.com/wp-content/uploads/2025/07/484.png
     ✅ Script verify_links_integrity.py implementado
           ✅ **HALLAZGOS**: 
        - ✅ **CORREGIDO**: 0 discrepancias de números (antes eran 3: #71, #77, #86)
        - ✅ **CORREGIDO**: 0 enlaces de descarga faltantes (antes eran 21)
        - 393 inconsistencias de dominio (normal: WordPress + iVoox)
        - Episodios 0-91: 82 con URL iVoox, 10 con URL WordPress
        - Episodios 92+: Mayoría con URL WordPress + descarga iVoox
        - Episodios 100-106: Usan blip.tv para descargas (normal)
      ✅ **CONCLUSIÓN**: Los enlaces son coherentes, las inconsistencias son esperadas por la evolución del podcast
      ✅ **CORREGIDO**: Todos los enlaces de descarga faltantes añadidos desde archivos HTML
      ✅ **CORREGIDO**: Todas las discrepancias de números corregidas con URLs correctas





## Próximos pasos:



[x] Extra ¿sacamos de web_playlist el número de canciones a un campo e introducimos esto en la BDD? Esto habria que hacerlo en el importador de podcasts.
    ✅ Implementado en rama feature/web-songs-count
    ✅ Nuevo campo web_songs_count añadido a la tabla podcasts
    ✅ Script SQL para migración en Supabase: migration/add_web_songs_count_field.sql
    ✅ Funciones update_web_info actualizadas en SQLite y Supabase
    ✅ WebExtractor actualizado para calcular automáticamente el número de canciones
    ✅ Scripts de migración y actualización: scripts/utils/migrate_web_songs_count.py y update_web_songs_count.py
    ✅ CLI web actualizado para mostrar el nuevo campo
    ✅ Compatible con ambas bases de datos (SQLite y Supabase)
      
[ ] Verificar la integridad de la Tabla songs en la BD

    - comprobamos que están todos los números de capítulo (veo que faltan algunos)
    - comprobamos que no hay números de canciones faltantes entre el primero y el último
        - si hemos extraido el número de canciones del podcast, comprobamos que coinciden
        - buscamos campos vacíos para revisar por qué no se han llenado.






[ ] Extraer los comentarios del nombre a un campo extra

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




# llamada a los scripts:

# backup de la BDD
clear && uv run python 