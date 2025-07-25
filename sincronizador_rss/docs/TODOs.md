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
    web_playlist:
    [{"position": 1, "artist": "the beatles", "title": "rain"}, {"position": 2, "artist": "the doors", "title": "wintertime love"}, {"position": 3, "artist": "joni mitchell", "title": "don\u2019t interrupt the sorrow"}, {"position": 4, "artist": "scott walker", "title": "get behind me"}, {"position": 5, "artist": "jefferson airplane", "title": "greasy heart"}, {"position": 6, "artist": "chic", "title": "happy man"}, {"position": 7, "artist": "ian dury & the blockheads", "title": "hit me with your rhythm stick"}, {"position": 8, "artist": "cowboy junkies", "title": "murder tonight, in the trailer park"}, {"position": 9, "artist": "the grateful dead", "title": "stella blue"}, {"position": 10, "artist": "r.e.m.", "title": "9-9"}, {"position": 11, "artist": "free", "title": "remember"}, {"position": 12, "artist": "the four tops", "title": "bernadette"}, {"position": 13, "artist": "yes", "title": "beyond and before"}, {"position": 14, "artist": "roxy music", "title": "2hb"}, {"position": 15, "artist": "can", "title": "sing swan song"}, {"position": 16, "artist": "david bowie", "title": "lady grinning soul"}, {"position": 17, "artist": "rod stewart", "title": "country comfort"}, {"position": 18, "artist": "love", "title": "andmoreagain"}, {"position": 19, "artist": "the byrds", "title": "everybody\u2019s been burned"}, {"position": 20, "artist": "julian cope", "title": "fear loves this place"}, {"position": 21, "artist": "john cale", "title": "fear is a man\u2019s best friend"}, {"position": 22, "artist": "the beatles", "title": "i want you (she\u2019s so heavy)"}]

    rss_playlist:
    the beatles · rain  ::  the doors · wintertime love  ::  joni mitchell · don't interrupt the sorrow  ::  scott walker · get behind me  ::  jefferson airplane · greasy heart  ::  chic · happy man  ::  ian dury & the blockheads · hit me with your rhythm stick  ::  cowboy junkies · murder tonight, in the trailer park  ::  the grateful dead · stella blue  ::  r.e.m. · 9-9  ::  free · remember::  the four tops · bernadette  ::  yes · beyond and before  ::  roxy music · 2hb  ::  can · sing swan song  ::  david bowie · lady grinning soul  ::  rod stewart · country comfort  ::  love · andmoreagain  ::  the byrds · everybody's been burned  ::  julian cope · fear loves this place  ::  john cale · fear is a man's best friend  ::  the beatles · i want you (she's so heavy)      

:::::: invita a Popcasting a café https://ko-fi.com/popcasting


Cómo podríamos asegurarnos de extraer los datos chequando en ambas tablas? ¿merece la pena cambiar el formato de rss antes de guardarlo? ¿dónde y cómo hacemos el proceso de extracción y almacenamiento?








