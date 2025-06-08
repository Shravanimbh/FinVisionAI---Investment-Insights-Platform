import sqlite3

# Connect to your database
conn = sqlite3.connect('investment_schemes.db')
cursor = conn.cursor()

# Check if 'gov_schemes' table exists
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='gov_schemes';")
table_exists = cursor.fetchone()

if table_exists:
    print("✅ 'gov_schemes' table found.\n")

    # Show some rows
    cursor.execute("SELECT * FROM gov_schemes LIMIT 5;")
    rows = cursor.fetchall()

    if rows:
        print("📄 Sample records:")
        for row in rows:
            print(row)
    else:
        print("⚠️ Table is empty!")
else:
    print("❌ Table 'gov_schemes' does not exist!")

conn.close()

