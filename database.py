import sqlite3

# Kumonekta sa database (gagawa ito ng bagong file kung wala pa)
conn = sqlite3.connect("flashcards.db")
cursor = conn.cursor()

# Gumawa ng tables para sa Decks at Cards
cursor.execute('''
    CREATE TABLE IF NOT EXISTS decks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS cards (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        deck_id INTEGER NOT NULL,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE
    )
''')

conn.commit()  # I-save ang changes
conn.close()   # Isara ang koneksyon

print("Database and tables created successfully.")
