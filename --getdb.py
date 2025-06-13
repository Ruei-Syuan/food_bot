# import sqlite3
# conn = sqlite3.connect('LINEBOT_DB.db')  # 確保使用正確的資料庫檔案名稱
# cursor = conn.cursor()

# cursor.execute('''
# CREATE TABLE food_map (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     keyword TEXT UNIQUE,
#     title TEXT,
#     address TEXT,
#     latitude TEXT,
#     longitude TEXT
# )
# ''')

# conn.commit()
# conn.close()
# print("Table `food_map` created successfully!")