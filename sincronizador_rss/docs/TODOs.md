**25/07/2025**

[x] Limpiar los enlaces de web_playlist
    ✅ **COMPLETADO**: Se han limpiado 284 enlaces guardados incorrectamente como canciones
    ✅ **COMPLETADO**: Se ha verificado que web_songs_count coincide con el número real de canciones
    ✅ **COMPLETADO**: Se han analizado TODAS las filas (486 episodios) para detectar enlaces
    ✅ **COMPLETADO**: Se han creado scripts de limpieza y verificación automática
    ✅ **COMPLETADO**: Coherencia final: 100% (486/486 episodios coherentes)
    ✅ **COMPLETADO**: 7,456 canciones válidas, 0 enlaces restantes
    ✅ **COMPLETADO**: Documentación completa en docs/LIMPIEZA_WEB_PLAYLIST_COMPLETADA.md
    ✅ **COMPLETADO**: Scripts reutilizables para mantenimiento futuro


    ✅ **COMPLETADO**: Reescaneo de episodios sin web_playlist
    ✅ **COMPLETADO**: Se han procesado 20 episodios exitosamente
    ✅ **COMPLETADO**: Total de 318 canciones extraídas de WordPress
    ✅ **COMPLETADO**: Búsqueda inteligente de fechas implementada para episodios con discrepancias
    ✅ **COMPLETADO**: Mejoras en parsing de caracteres Unicode y elementos HTML
    ✅ **COMPLETADO**: Script `overwrite_episode.py` desarrollado y probado
    ✅ **COMPLETADO**: Documentación completa del proceso

    Episodios procesados:
    - 95: 10 canciones (web_playlist desde `<span>`)
    - 138: 13 canciones (web_playlist desde `<p>`)
    - 197: 18 canciones (web_playlist desde `<p>`)
    - 206: 14 canciones (web_playlist desde `<p>`)
    - 207: 17 canciones (web_playlist desde `<p>`, búsqueda inteligente de fechas)
    - 209: 12 canciones (web_playlist desde `<p>`)
    - 210: 12 canciones (web_playlist desde `<p>`)
    - 216: 12 canciones (web_playlist desde `<p>`)
    - 233: 15 canciones (web_playlist desde `<p>`, búsqueda inteligente de fechas)
    - 260: 16 canciones (web_playlist desde `<p>`)
    - 261: 15 canciones (web_playlist desde `<p>`)
    - 267: 24 canciones (web_playlist desde `<p>`)
    - 274: 18 canciones (web_playlist desde `<p>`)
    - 277: 20 canciones (web_playlist desde `<p>`, búsqueda inteligente de fechas)
    - 282: 14 canciones (web_playlist desde `<p>`)
    - 288: 12 canciones (web_playlist desde `<p>`)
    - 290: 17 canciones (web_playlist desde `<p>`, búsqueda inteligente de fechas)
    - 293: 25 canciones (web_playlist desde `<p>`)
    - 295: 13 canciones (web_playlist desde `<p>`)
    - 304: 12 canciones (web_playlist desde `<p>`)

    Documentación completa en docs/REESCANEO_EPISODIOS_COMPLETADO.md

________________________________________________________________________________________________________________________

**26/07/2025**


7:45 - 9:15

[x] ✅ **COMPLETADO**: Sistema completo de procesamiento y almacenamiento de canciones
    ✅ **COMPLETADO**: Refactorización de la lógica de procesamiento de canciones en componente SongProcessor
    ✅ **COMPLETADO**: Creación de src/components/song_processor.py con responsabilidades especializadas
    ✅ **COMPLETADO**: Integración completa en main.py para procesamiento automático de canciones
    ✅ **COMPLETADO**: Script de relleno histórico scripts/backfill_songs.py para regenerar datos
    ✅ **COMPLETADO**: Limpieza preventiva de campos problemáticos (duration) en procesadores
    ✅ **COMPLETADO**: Pruebas exhaustivas de funcionalidad con episodios 483, 484, 485
    ✅ **COMPLETADO**: Resolución de problemas de esquema de base de datos
    ✅ **COMPLETADO**: Documentación completa del proceso y arquitectura

    **Arquitectura implementada:**
    - **SongProcessor**: Componente especializado para procesamiento de canciones
    - **Lógica de decisión**: Prioriza web_playlist sobre rss_playlist
    - **Validación de datos**: Verificación de integridad de canciones
    - **Almacenamiento en lote**: Método insert_songs_batch en DatabaseManager
    - **Limpieza preventiva**: Remoción automática de campos problemáticos

    **Pruebas realizadas:**
    1. ✅ Borrado completo de tabla songs y repoblación exitosa
    2. ✅ Procesamiento de episodio 483 desde datos RSS (funcionó correctamente)
    3. ✅ Procesamiento de episodio 484 desde datos web (funcionó correctamente)
    4. ✅ Integración en main.py con episodio 485 (funcionó correctamente)
    5. ✅ Relleno histórico completo de 486 episodios (7,733 canciones)

    **Problemas resueltos:**
    - ✅ Error de esquema: Campo "duration" incompatible con tabla songs
    - ✅ Limpieza de 93 playlists con campos problemáticos
    - ✅ Implementación de limpieza preventiva en RSSDataProcessor y WordPressDataProcessor
    - ✅ Resolución de problemas de importación en componentes

    **Resultados finales:**
    - 📻 **486 podcasts** procesados exitosamente
    - 🎵 **7,733 canciones** almacenadas en total
    - ✅ **0 errores** en el procesamiento final
    - 🛠️ **Scripts reutilizables** para mantenimiento futuro

11:15

[x] ✅ **COMPLETADO**: Cliente para Synology NAS
    ✅ **COMPLETADO**: Cliente simplificado y funcional en src/components/synology_client.py
    ✅ **COMPLETADO**: Autenticación con API File Station de Synology
    ✅ **COMPLETADO**: Subida de archivos con manejo correcto de multipart/form-data
    ✅ **COMPLETADO**: Listado de carpetas compartidas y contenido
    ✅ **COMPLETADO**: Lectura de archivos de texto
    ✅ **COMPLETADO**: Context manager para gestión automática de sesiones
    ✅ **COMPLETADO**: Configuración desde variables de entorno (.env)
    ✅ **COMPLETADO**: Manejo robusto de errores y timeouts
    ✅ **COMPLETADO**: Pruebas exhaustivas con carpeta popcasting_marilyn
    ✅ **COMPLETADO**: Documentación completa del cliente

    **Funcionalidades implementadas:**
    - **Autenticación**: Login/logout automático con token de sesión
    - **Upload**: Subida de archivos a carpetas compartidas específicas
    - **List**: Listado de contenido de carpetas y carpetas compartidas
    - **Read**: Lectura de archivos de texto del NAS
    - **Context Manager**: Uso seguro con `with SynologyClient() as client:`

    **Configuración requerida en .env:**
    ```
    SYNOLOGY_IP=192.168.1.143
    SYNOLOGY_PORT=5000
    SYNOLOGY_USER=usuario
    SYNOLOGY_PASS=contraseña
    SYNOLOGY_SHARED_FOLDER=/popcasting_marilyn
    ```

    **Pruebas realizadas:**
    - ✅ Conexión y autenticación exitosa
    - ✅ Descubrimiento de carpetas compartidas (home, popcasting_marilyn)
    - ✅ Subida de archivos de prueba exitosa
    - ✅ Verificación de contenido y lectura de archivos
    - ✅ Limpieza automática de archivos temporales


[x] Almacenar los mp3 en el NAS, haciendo un log detallado de los archivos que se han subido y los que no se han podido subir. 
    ✅ **COMPLETADO**: AudioManager para Popcasting
    ✅ **COMPLETADO**: Descarga automática de MP3 desde URLs
    ✅ **COMPLETADO**: Subida automática al NAS Synology con renombrado
    ✅ **COMPLETADO**: Verificación de duplicados y limpieza de temporales
    ✅ **COMPLETADO**: 475 episodios descargados (0-485) de 486 totales
    ✅ **COMPLETADO**: Migración completa a Supabase (486 episodios)
    ✅ **COMPLETADO**: Tests implementados y documentación actualizada
    ✅ **COMPLETADO**: Optimización de comprobación de archivos en NAS usando API getinfo (sin logs masivos)

    **Estado actual:**
    - **Total episodios**: 486 en BD
    - **Descargados**: 475 en NAS
    - **Pendiente**: Solo episodio 486 cuando esté disponible

    **Optimización implementada:**
    - **Antes**: Se listaban todos los archivos MP3 (474 archivos) para verificar existencia
    - **Ahora**: Solo se consulta la API para archivos específicos usando getinfo
    - **Resultado**: Logs limpios, proceso más rápido y eficiente

[ ] 🚀 **PENDIENTE**: Mejoras AudioManager
    - [ ] Procesamiento por lotes automático para episodios faltantes
    - [ ] Verificación de integridad de archivos descargados
    - [ ] Interfaz CLI para gestión de audio
    - [ ] Descarga paralela de múltiples episodios

[ ] 📊 **PENDIENTE**: Sistema de Monitoreo
    - [ ] Dashboard web para monitorear estado del catálogo
    - [ ] Alertas automáticas cuando falten episodios
    - [ ] Métricas de descarga (velocidad, éxito, errores)

[ ] 📱 **PENDIENTE**: Interfaz de Usuario
    - [ ] API REST para gestión remota
    - [ ] Interfaz web para administración
    - [ ] Notificaciones por email/Slack

    **Archivos principales:**
    - `src/components/audio_manager.py` - Componente principal
    - `src/components/README_AUDIO_MANAGER.md` - Documentación
    - `tests/test_audio_manager.py` - Tests

    **Próximo objetivo**: Procesamiento por lotes automático





[ ] Añadir la duración de los mp3 a la tabla podcasts en supabase en un campo nuevo mp3_duration. si la información está disponible en el mp3 la usamos, si no usamos la libreria f







________________________________________________________________________________________________________________________


## TODOs


[ ] Borrar los archivos antiguos del proyecto, dejar sólo los de sincronizador_rss y ordenarlo




[ ] mandar mail con las actualizaciones y los errores




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

[ ] Integrar cliente Synology con el proyecto principal
    - Backup automático de base de datos a NAS
    - Subida automática de archivos generados
    - Sincronización de logs y reportes
    - Configuración centralizada en services/config.py
    - Integración con el sistema de logging existente

[ ] Mejorar cliente Synology NAS
    - Soporte para subida de múltiples archivos
    - Barra de progreso durante subidas
    - Verificación de integridad de archivos (checksum)
    - Soporte para autenticación de dos factores
    - Configuración de carpetas por defecto personalizable
    - Logs detallados de operaciones
    - Retry automático en caso de fallos de red

[ ] Optimizaciones y mejoras técnicas
    - Cache de consultas frecuentes
    - Optimización de índices en Supabase
    - Sistema de backup automático
    - Monitoreo y alertas de rendimiento


________________________________________________________________________________________________________________________



## DATOS

- Supabase. https://supabase.com/dashboard/project/ndhmlymnbrewflharfmr/
- Synology NAS. https://192.168.1.100:5000/

