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
        date TEXT NOT NULL UNIQUE,
        url TEXT,
        download_url TEXT,
        file_size INTEGER,
        program_number TEXT
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
