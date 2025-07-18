
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










- Extraer información de la web de cada episodio
- leer el feed periodicamente y añadir sólo los episodios nuevos
- probar la BD en supabase
- crear el front del buscador de canciones
- extraer información extra de las canciones de las api de spotify, Discogs, etc.
- Transcribir los episodios de popcasting
- Añadir el comentario de cada canción de la transcripción a la tabla de canciones