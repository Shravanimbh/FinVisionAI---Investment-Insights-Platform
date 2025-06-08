import sqlite3

conn = sqlite3.connect("investment_schemes.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS gov_schemes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    description TEXT,
    category TEXT,
    risk_level TEXT,
    eligibility TEXT,
    return_rate REAL,
    tenure TEXT,
    official_link TEXT
)
""")

# Optionally insert some dummy data
schemes = [
    ("Public Provident Fund (PPF)", "Long-term savings with tax benefits.", "Retirement", "Low", "18+", 7.1, "15 years", "https://www.india.gov.in/public-provident-fund-ppf"),
    ("National Pension System (NPS)", "Pension-focused investment with moderate returns.", "Pension", "Medium", "18-60", 8.0, "Until 60 years", "https://www.npscra.nsdl.co.in/"),
    ("Sukanya Samriddhi Yojana", "Savings for girl child's education and marriage.", "Education", "Low", "10-18", 7.6, "21 years", "https://www.india.gov.in/sukanya-samriddhi-yojana"),
    ("Senior Citizens' Savings Scheme", "Secure income for senior citizens.", "Retirement", "Low", "60+", 8.2, "5 years", "https://www.india.gov.in/senior-citizens-savings-scheme"),
    
    # ✅ New Scheme for 60+ with Medium risk and Pension goal
    ("Pension Guarantee Scheme", "Pension scheme designed for citizens aged 60 and above.", "Pension", "Medium", "60+", 7.5, "Lifetime", "https://example.com/pension-guarantee")
]

cursor.executemany("""
INSERT INTO gov_schemes (name, description, category, risk_level, eligibility, return_rate, tenure, official_link)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", schemes)

conn.commit()
conn.close()
print("✅ Table created and sample data inserted.")
