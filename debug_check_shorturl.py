#!/usr/bin/env python3
"""
Script para mostrar cómo se están guardando los links con 'shorturl' en la base de datos
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services import database as db


def check_shorturl_links():
    conn = db.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.title, p.date, el.text, el.url
        FROM extra_links el
        JOIN podcasts p ON el.podcast_id = p.id
        WHERE el.url LIKE '%shorturl%'
        ORDER BY p.date DESC
        LIMIT 10
    """)
    results = cursor.fetchall()
    print("=== LINKS CON 'shorturl' EN LA BASE DE DATOS ===")
    for row in results:
        print(f"\n📻 {row['title']} ({row['date']})")
        print(f"   Texto: '{row['text']}'")
        print(f"   URL: {row['url']}")
    conn.close()


if __name__ == "__main__":
    check_shorturl_links()
