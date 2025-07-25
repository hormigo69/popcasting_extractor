[ ] Rellenar la tabla de songs con los datos de los episodios de la tabla podcasts  
    esto no sé muy bien cómo hacerlo. tenemos tres datos en la tabla podcasts de los que salen los datos de la tabla songs:
    - web_playlist
    - rss_playlist
    - web_songs_count

    En la tabla de songs tenemos que rellenar:
    campos obvios:
    - id: ID único de la canción | lo genera la base de datos
    - created_at: Fecha de creación | lo genera la base de datos
    - podcast_id: ID del episodio (FK) | lo metemos desde la tabla podcasts

    campos que no son obvios:
    - title: Título de la canción | extraído de la web_playlist o rss_playlist
    - artist: Artista de la canción | extraído de la web_playlist o rss_playlist
    - position: Posición en el episodio | extraído de la web_playlist o rss_playlist

    Los datos de ambas playlists deberían de coincidir. Un tema es que están en formatos difereentes:
    


Cómo podríamos asegurarnos de extraer los datos chequando en ambas tablas? ¿merece la pena cambiar el formato de rss antes de guardarlo? ¿dónde y cómo hacemos el proceso de extracción y almacenamiento?



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