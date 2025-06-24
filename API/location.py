import os
import sqlite3
import shutil


# 取得連線：Render 上的 SQLite 寫入路徑需在 /tmp/
def get_connection(filename="LINEBOT_DB.db"):
    tmp_db_path = os.path.join("/tmp", filename)

    # 如果 /tmp 中沒有，就從專案根目錄複製一份過去（唯讀 → 可寫）
    if not os.path.exists(tmp_db_path):
        if os.path.exists(filename):
            shutil.copy(filename, tmp_db_path)
        else:
            # 若本地也沒有，就在 /tmp 中建立新資料庫
            open(tmp_db_path, 'a').close()

    return sqlite3.connect(tmp_db_path)

# 建立資料表
def create_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS food_map (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            address TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            keyword TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# 儲存資料到 DB
def save_to_db(title, address, latitude, longitude, keyword):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO food_map (title, address, latitude, longitude, keyword)
        VALUES (?, ?, ?, ?, ?)
    ''', (title, address, float(latitude), float(longitude), keyword))
    conn.commit()
    conn.close()

# 根據關鍵字模糊搜尋地點
def get_location(text):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT title, address, latitude, longitude
        FROM food_map
        WHERE keyword LIKE ?
    ''', ('%' + text + '%',))
    rows = cursor.fetchall()
    conn.close()

    if rows:
        results = []
        for row in rows:
            results.append({
                'title': row[0],
                'address': row[1],
                'latitude': row[2],
                'longitude': row[3]
            })
        return results[0] if len(results) == 1 else results
    else:
        return False
