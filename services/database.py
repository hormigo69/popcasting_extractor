import sqlite3
from pathlib import Path

# La base de datos estará en el directorio raíz del proyecto
DB_PATH = Path(__file__).parent.parent / "popcasting.db"


def get_db_connection():
    """Crea y devuelve una conexión a la base de datos."""
    conn = sqlite3.connect(DB_PATH)
    # Usar el modo Row para poder acceder a las columnas por nombre
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    """
    Inicializa la base de datos creando las tablas si no existen.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Crear tabla de podcasts
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS podcasts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        date DATE NOT NULL UNIQUE,
        url TEXT,
        download_url TEXT,
        file_size INTEGER,
        program_number INTEGER
    );
    """)

    # Crear tabla de canciones
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS songs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        artist TEXT NOT NULL,
        position INTEGER,
        podcast_id INTEGER,
        FOREIGN KEY (podcast_id) REFERENCES podcasts (id)
    );
    """)

    # Crear tabla de links extras
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS extra_links (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        text TEXT NOT NULL,
        url TEXT NOT NULL,
        podcast_id INTEGER,
        FOREIGN KEY (podcast_id) REFERENCES podcasts (id)
    );
    """)

    # Crear un índice para buscar podcasts por fecha más rápidamente
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_podcasts_date ON podcasts(date);")

    # Migrar base de datos existente si es necesario
    migrate_database_if_needed(cursor)

    conn.commit()
    conn.close()


def migrate_database_if_needed(cursor):
    """Migra la base de datos si es necesario añadir nuevas columnas"""
    try:
        # Verificar si existe la columna download_url
        cursor.execute("PRAGMA table_info(podcasts)")
        columns = [column[1] for column in cursor.fetchall()]

        # Añadir download_url si no existe
        if "download_url" not in columns:
            cursor.execute("ALTER TABLE podcasts ADD COLUMN download_url TEXT")
            print("✅ Añadida columna download_url a la tabla podcasts")

        # Añadir file_size si no existe
        if "file_size" not in columns:
            cursor.execute("ALTER TABLE podcasts ADD COLUMN file_size INTEGER")
            print("✅ Añadida columna file_size a la tabla podcasts")

        # Añadir campos para información de la web
        if "wordpress_url" not in columns:
            cursor.execute("ALTER TABLE podcasts ADD COLUMN wordpress_url TEXT")
            print("✅ Añadida columna wordpress_url a la tabla podcasts")

        if "cover_image_url" not in columns:
            cursor.execute("ALTER TABLE podcasts ADD COLUMN cover_image_url TEXT")
            print("✅ Añadida columna cover_image_url a la tabla podcasts")

        if "web_extra_links" not in columns:
            cursor.execute("ALTER TABLE podcasts ADD COLUMN web_extra_links TEXT")
            print("✅ Añadida columna web_extra_links a la tabla podcasts")

        if "web_playlist" not in columns:
            cursor.execute("ALTER TABLE podcasts ADD COLUMN web_playlist TEXT")
            print("✅ Añadida columna web_playlist a la tabla podcasts")

        if "web_songs_count" not in columns:
            cursor.execute("ALTER TABLE podcasts ADD COLUMN web_songs_count INTEGER")
            print("✅ Añadida columna web_songs_count a la tabla podcasts")

        if "last_web_check" not in columns:
            cursor.execute("ALTER TABLE podcasts ADD COLUMN last_web_check TEXT")
            print("✅ Añadida columna last_web_check a la tabla podcasts")

    except Exception as e:
        print(f"⚠️  Error durante la migración de la base de datos: {e}")


def add_podcast_if_not_exists(
    title: str,
    date: str,
    url: str,
    program_number: str,
    download_url: str = None,
    file_size: int = None,
) -> int:
    """
    Añade un nuevo podcast a la base de datos si no existe uno con la misma fecha.
    Devuelve el ID del podcast (ya sea nuevo o existente).
    """
    # Validar y convertir tipos
    import re
    from datetime import datetime

    # Validar program_number
    if program_number:
        # Limpiar caracteres no numéricos
        cleaned_number = re.sub(r"[^\d]", "", str(program_number))
        if cleaned_number:
            program_number = int(cleaned_number)
        else:
            program_number = None

    # Validar date
    if date:
        try:
            # Intentar parsear la fecha
            dt = datetime.strptime(date, "%Y-%m-%d")
            date = dt.strftime("%Y-%m-%d")
        except ValueError:
            # Si no es formato YYYY-MM-DD, intentar otros formatos
            date_formats = ["%d/%m/%Y", "%d.%m.%Y", "%Y/%m/%d", "%d-%m-%Y"]
            for fmt in date_formats:
                try:
                    dt = datetime.strptime(date, fmt)
                    date = dt.strftime("%Y-%m-%d")
                    break
                except ValueError:
                    continue
            else:
                # Si no se puede parsear, usar fecha por defecto
                date = "2005-01-01"

    conn = get_db_connection()
    cursor = conn.cursor()

    # Primero, comprobar si ya existe un podcast con esa fecha
    cursor.execute("SELECT id FROM podcasts WHERE date = ?", (date,))
    result = cursor.fetchone()

    if result:
        podcast_id = result["id"]
        # Actualizar información de links si no estaba disponible antes
        if download_url or file_size:
            update_fields = []
            update_values = []
            if download_url:
                update_fields.append("download_url = ?")
                update_values.append(download_url)
            if file_size:
                update_fields.append("file_size = ?")
                update_values.append(file_size)

            if update_fields:
                update_values.append(podcast_id)
                cursor.execute(
                    f"UPDATE podcasts SET {', '.join(update_fields)} WHERE id = ?",
                    update_values,
                )
                conn.commit()
    else:
        # Si no existe, lo insertamos
        cursor.execute(
            "INSERT INTO podcasts (title, date, url, program_number, download_url, file_size) VALUES (?, ?, ?, ?, ?, ?)",
            (title, date, url, program_number, download_url, file_size),
        )
        conn.commit()
        podcast_id = cursor.lastrowid

    conn.close()
    return podcast_id


def add_song(podcast_id: int, title: str, artist: str, position: int):
    """Añade una canción asociada a un podcast."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO songs (podcast_id, title, artist, position) VALUES (?, ?, ?, ?)",
        (podcast_id, title, artist, position),
    )
    conn.commit()
    conn.close()


def delete_songs_by_podcast_id(podcast_id: int):
    """Borra todas las canciones asociadas a un ID de podcast."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM songs WHERE podcast_id = ?", (podcast_id,))

    conn.commit()
    conn.close()


def add_extra_link(podcast_id: int, text: str, url: str):
    """Añade un link extra asociado a un podcast."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO extra_links (podcast_id, text, url) VALUES (?, ?, ?)",
        (podcast_id, text, url),
    )
    conn.commit()
    conn.close()


def delete_extra_links_by_podcast_id(podcast_id: int):
    """Borra todos los links extras asociados a un ID de podcast."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM extra_links WHERE podcast_id = ?", (podcast_id,))

    conn.commit()
    conn.close()


def get_extra_links_by_podcast_id(podcast_id: int) -> list:
    """Obtiene todos los links extras de un podcast específico."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT text, url FROM extra_links WHERE podcast_id = ? ORDER BY id",
        (podcast_id,),
    )

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def search_songs(query: str) -> list:
    """
    Busca canciones por título o artista.
    La búsqueda no distingue mayúsculas/minúsculas.
    Devuelve una lista de diccionarios con la canción y la info del podcast.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # El término de búsqueda se formatea con '%' para usar con LIKE
    search_term = f"%{query}%"

    cursor.execute(
        """
        SELECT
            s.title as song_title,
            s.artist,
            s.position,
            p.title as podcast_title,
            p.date as podcast_date,
            p.program_number
        FROM
            songs s
        JOIN
            podcasts p ON s.podcast_id = p.id
        WHERE
            s.title LIKE ? OR s.artist LIKE ?
        ORDER BY
            p.date DESC
    """,
        (search_term, search_term),
    )

    results = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return results


def search_by_artist(artist_query: str) -> list:
    """
    Busca todas las canciones de un artista específico.
    La búsqueda no distingue mayúsculas/minúsculas.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    search_term = f"%{artist_query}%"

    cursor.execute(
        """
        SELECT
            s.title as song_title,
            s.artist,
            s.position,
            p.title as podcast_title,
            p.date as podcast_date,
            p.program_number
        FROM
            songs s
        JOIN
            podcasts p ON s.podcast_id = p.id
        WHERE
            s.artist LIKE ? COLLATE NOCASE
        ORDER BY
            p.date DESC
    """,
        (search_term,),
    )

    results = [dict(row) for row in cursor.fetchall()]

    conn.close()
    return results


def get_all_podcasts() -> list:
    """
    Obtiene todos los podcasts ordenados por fecha (más recientes primero).
    Devuelve una lista de tuplas (id, title, date, url, program_number).
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, date, url, download_url, file_size, program_number
        FROM podcasts
        ORDER BY date DESC
    """)

    results = cursor.fetchall()

    conn.close()
    return results


def get_songs_by_podcast_id(podcast_id: int) -> list:
    """
    Obtiene todas las canciones de un podcast específico.
    Devuelve una lista de tuplas (id, podcast_id, artist, title, position).
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, podcast_id, artist, title, position
        FROM songs
        WHERE podcast_id = ?
        ORDER BY position
    """,
        (podcast_id,),
    )

    results = cursor.fetchall()

    conn.close()
    return results


def get_podcast_by_id(podcast_id: int) -> dict:
    """
    Obtiene un podcast específico por su ID.
    Devuelve un diccionario con la información del podcast o None si no existe.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, title, date, url, program_number
        FROM podcasts
        WHERE id = ?
    """,
        (podcast_id,),
    )

    result = cursor.fetchone()

    conn.close()
    return dict(result) if result else None


def songs_have_changed(podcast_id: int, new_songs: list) -> bool:
    """
    Compara las canciones existentes con las nuevas para detectar cambios.
    Devuelve True si hay cambios, False si son idénticas.
    """
    existing_songs = get_songs_by_podcast_id(podcast_id)

    # Si el número de canciones es diferente, hay cambios
    if len(existing_songs) != len(new_songs):
        return True

    # Comparar cada canción
    for i, existing_song in enumerate(existing_songs):
        new_song = new_songs[i]

        # Comparar artista, título y posición
        if (
            existing_song["artist"].lower() != new_song["artist"].lower()
            or existing_song["title"].lower() != new_song["song"].lower()
            or existing_song["position"] != new_song["position"]
        ):
            return True

    return False


def extra_links_have_changed(podcast_id: int, new_links: list) -> bool:
    """
    Compara los links extras existentes con los nuevos para detectar cambios.
    Devuelve True si hay cambios, False si son idénticos.
    El orden no importa, solo el contenido.
    """
    existing_links = get_extra_links_by_podcast_id(podcast_id)

    # Si el número de links es diferente, hay cambios
    if len(existing_links) != len(new_links):
        return True

    # Crear sets para comparación independiente del orden
    existing_set = set()
    new_set = set()

    # Añadir links existentes al set
    for link in existing_links:
        existing_set.add((link["text"].lower(), link["url"].lower()))

    # Añadir links nuevos al set
    for link in new_links:
        new_set.add((link["text"].lower(), link["url"].lower()))

    # Si los sets son diferentes, hay cambios
    return existing_set != new_set


def update_songs_if_changed(podcast_id: int, new_songs: list) -> bool:
    """
    Actualiza las canciones solo si han cambiado.
    Devuelve True si se actualizaron, False si no había cambios.
    """
    if not songs_have_changed(podcast_id, new_songs):
        return False

    # Si hay cambios, borrar las existentes y añadir las nuevas
    delete_songs_by_podcast_id(podcast_id)
    for song in new_songs:
        add_song(
            podcast_id=podcast_id,
            title=song["song"],
            artist=song["artist"],
            position=song["position"],
        )
    return True


def update_extra_links_if_changed(podcast_id: int, new_links: list) -> bool:
    """
    Actualiza los links extras solo si han cambiado.
    Devuelve True si se actualizaron, False si no había cambios.
    """
    if not extra_links_have_changed(podcast_id, new_links):
        return False

    # Si hay cambios, borrar los existentes y añadir los nuevos
    delete_extra_links_by_podcast_id(podcast_id)
    for link in new_links:
        add_extra_link(
            podcast_id=podcast_id,
            text=link["text"],
            url=link["url"],
        )
    return True


def update_web_info(
    podcast_id: int,
    wordpress_url: str = None,
    cover_image_url: str = None,
    web_extra_links: str = None,
    web_playlist: str = None,
    web_songs_count: int = None,
):
    """
    Actualiza la información extraída de la web para un podcast.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    update_fields = []
    update_values = []

    if wordpress_url is not None:
        update_fields.append("wordpress_url = ?")
        update_values.append(wordpress_url)

    if cover_image_url is not None:
        update_fields.append("cover_image_url = ?")
        update_values.append(cover_image_url)

    if web_extra_links is not None:
        update_fields.append("web_extra_links = ?")
        update_values.append(web_extra_links)

    if web_playlist is not None:
        update_fields.append("web_playlist = ?")
        update_values.append(web_playlist)

    if web_songs_count is not None:
        update_fields.append("web_songs_count = ?")
        update_values.append(web_songs_count)

    # Siempre actualizar la fecha del último check
    from datetime import datetime

    update_fields.append("last_web_check = ?")
    update_values.append(datetime.now().isoformat())

    if update_fields:
        update_values.append(podcast_id)
        cursor.execute(
            f"UPDATE podcasts SET {', '.join(update_fields)} WHERE id = ?",
            update_values,
        )
        conn.commit()

    conn.close()


def get_podcasts_without_web_info() -> list:
    """
    Obtiene todos los podcasts que no tienen información de la web o no han sido verificados recientemente.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, date, program_number, wordpress_url, last_web_check
        FROM podcasts
        WHERE wordpress_url IS NULL OR last_web_check IS NULL
        ORDER BY date DESC
    """)

    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return results


def get_podcast_web_info(podcast_id: int) -> dict:
    """
    Obtiene la información de la web para un podcast específico.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT wordpress_url, cover_image_url, web_extra_links, web_playlist, web_songs_count, last_web_check
        FROM podcasts
        WHERE id = ?
    """,
        (podcast_id,),
    )

    result = cursor.fetchone()
    conn.close()

    if result:
        return dict(result)
    return None
