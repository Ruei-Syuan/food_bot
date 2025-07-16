from functools import wraps

from flask import Flask, g, current_app
import psycopg2
from psycopg2._psycopg import connection as Connection
from psycopg2._psycopg import cursor as Cursor


def get_connection() -> Connection:
    if 'db_conn' not in g:
        g.db_conn = current_app.db_connect()

    return g.db_conn


def db_cursor(
    method: callable = None,
    commit = False,
):
    """Inject cursor (context managed) into function"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if commit:
                g.commit = True
            
            with get_connection().cursor() as cursor:
                return func(cursor, *args, **kwargs, cursor=cursor)

        return wrapper
    
    return decorator(method) if method else decorator


@db_cursor(commit=True)
def store_record(
    title: str,
    address: str,
    latitude: float,
    longitude: float,
    keyword: str,
    *,
    cursor: Cursor,
):
    cursor.execute('''
        INSERT INTO food_map (title, address, latitude, longitude, keyword)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (title, keyword) DO NOTHING
    ''', (title, address, latitude, longitude, keyword))
    return


@db_cursor
def query_record(
    text: str,
    *,
    cursor: Cursor,
):
    cursor.execute('''
        SELECT title, address, latitude, longitude
        FROM food_map
        WHERE keyword ILIKE %s
    ''', ('%' + text + '%',))

    rows = cursor.fetchall()

    if not rows:
        return list()
    
    return rows[0] if len(rows) == 1 else rows


def init_app(app: Flask):
    # DB connection factory
    app.db_connect = lambda: psycopg2.connect(
        host     = app.config["DB_HOST"],
        port     = app.config["DB_PORT"],
        database = app.config["DB_DATABASE"],
        user     = app.config["DB_USER"],
        password = app.config["DB_PASSWORD"],
    )

    def close_connection():
        if not (conn := g.pop('db_conn', None)):
            return
        
        if g.pop('commit', False):
            conn.commit()
        
        conn.close()

    app.after_request(close_connection)

    # Create table at initialization
    with (
        app.db_connect() as conn,
        conn.cursor() as cursor,
    ):
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS food_map (
                id SERIAL PRIMARY KEY,
                title TEXT NOT NULL,
                address TEXT NOT NULL,
                latitude FLOAT NOT NULL,
                longitude FLOAT NOT NULL,
                keyword TEXT NOT NULL
            )
        ''')
    conn.close()

    return
