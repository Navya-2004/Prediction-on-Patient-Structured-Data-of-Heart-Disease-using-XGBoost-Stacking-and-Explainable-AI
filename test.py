import mysql.connector

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Navya1711@",
        port=3307,
        database="HeartDisease"
    )
    print("✅ Database Connected Successfully!")
except Exception as e:
    print("❌ Error:", e)