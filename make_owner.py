import sqlite3

DB_PATH = "database/artbazar.db"

# 👉 ВСТАВЬ СВОЙ telegram_id
OWNER_TELEGRAM_ID = 6444576072  # <-- поменяй если нужно

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

cur.execute(
    "UPDATE users SET role = 'owner' WHERE telegram_id = ?",
    (OWNER_TELEGRAM_ID,)
)

conn.commit()
conn.close()

print("✅ OWNER назначен")
