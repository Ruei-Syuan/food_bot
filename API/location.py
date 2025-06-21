
import os
import sqlite3

# 設定資料庫路徑（Render 使用 /tmp）
DB_PATH = os.path.join("/tmp", "LINEBOT_DB.db")

# 如果資料庫不存在，可從原始位置複製過來
if not os.path.exists(DB_PATH):
    import shutil
    shutil.copy("LINEBOT_DB.db", DB_PATH)  # 假設你專案中原本有一份 readonly 資料庫

# 使用資料庫
def get_connection():
    return get_connection(DB_PATH)

# 建立資料表（如果尚未存在）
def create_table():
    conn = get_connection('LINEBOT_DB.db')
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
    
# 根據關鍵字搜尋資料庫
def get_location(text):
    conn = get_connection('LINEBOT_DB.db')  # 連接資料庫
    cursor = conn.cursor()

    # 查詢符合輸入內容的地點
    # cursor.execute("SELECT title, address, latitude, longitude FROM food_map WHERE keyword=?", (text,))
    # 改模糊比對
    cursor.execute("SELECT title, address, latitude, longitude FROM food_map WHERE keyword LIKE ?", ('%' + text + '%',))
    rows = cursor.fetchone()

    conn.close()  # 關閉連線

    # 如果有找到資料
    if rows:
        results = []
        for row in rows:
            result = {
                'title': row[0],
                'address': row[1],
                'latitude': row[2],
                'longitude': row[3]
            }
            results.append(result)
        
        # 如果只有一筆，回傳單一 dict；多筆則回傳 list
        if len(results) == 1:
            return results[0]
        else:
            return results
    else:
        return False
    
    # if row:
    #     return {'title': row[0], 'address': row[1], 'latitude': row[2], 'longitude': row[3]}
    # else:
    #     return False

def save_to_db(title, address, latitude, longitude, keyword):
    conn = get_connection('LINEBOT_DB.db')
    cursor = conn.cursor()
    cursor.execute('''
            INSERT INTO food_map (title, address, latitude, longitude, keyword)
            VALUES (?, ?, ?, ?, ?)
        ''', (title, address, float(latitude), float(longitude), keyword))
    # cursor.execute('INSERT INTO food_map (title, address) VALUES (?, ?)', (title, address))
    conn.commit()
    conn.close()