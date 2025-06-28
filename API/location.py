import os
import psycopg2
from psycopg2.extras import RealDictCursor

# 取得 PostgreSQL 連線（參數從環境變數取得）
def get_connection():
    conn = psycopg2.connect(
        host=os.getenv("PG_HOST"),
        port=os.getenv("PG_PORT"),
        database=os.getenv("PG_DATABASE"),
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD")
    )
    return conn

# 建立資料表
def create_table():
    conn = get_connection()
    cursor = conn.cursor()
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
    conn.commit()
    cursor.close()
    conn.close()

# 儲存資料到 PostgreSQL
# def save_to_db(title, address, latitude, longitude, keyword):
#     conn = get_connection()
#     cursor = conn.cursor()
#     cursor.execute('''
#         INSERT INTO food_map (title, address, latitude, longitude, keyword)
#         VALUES (%s, %s, %s, %s, %s)
#     ''', (title, address, float(latitude), float(longitude), keyword))
#     conn.commit()
#     cursor.close()
#     conn.close()
def save_to_db(title, address, latitude, longitude, keyword):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO food_map (title, address, latitude, longitude, keyword)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (title, keyword) DO NOTHING
        ''', (title, address, float(latitude), float(longitude), keyword))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

# 根據關鍵字模糊搜尋地點
def get_location(text):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute('''
        SELECT title, address, latitude, longitude
        FROM food_map
        WHERE keyword ILIKE %s
    ''', ('%' + text + '%',))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()

    if rows:
        return rows[0] if len(rows) == 1 else rows
    else:
        return False

# 測試用
# if __name__ == "__main__":
#     create_table()
#     save_to_db("麥當勞", "台北市信義路", 25.033964, 121.562321, "速食")
#     print(get_location("速食"))
