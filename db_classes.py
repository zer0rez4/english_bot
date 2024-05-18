import sqlite3


class DB():
    def __init__(self, path: str) -> None:
        self.conn = sqlite3.connect(f'english_bot/databases/{path}.db')
        self.cursor = self.conn.cursor()


    #функционал для добавления слова
    def check_word(self, word):
        self.cursor.execute(f"SELECT COUNT(*) FROM words WHERE russian_word = '{word}'")
        return self.cursor.fetchone()
    
    def add_word(self, word, translated_word, user_id):
        self.cursor.execute("INSERT INTO words (russian_word, english_word, creator_id) VALUES (?, ?, ?)", (word, translated_word, user_id))



    def __del__(self) -> None:
        self.conn.commit()
        self.conn.close()



# cursor.execute('''
#                CREATE TABLE words(
#                id INTEGER PRIMARY KEY,
#                russian_word TEXT,
#                english_word TEXT,
#                creator_name TEXT
#                )''')

# cursor.execute('''
#                CREATE TABLE user(
#                user_id INTEGER PRIMARY KEY,
#                started_word INTEGER,
#                guessed_word INTEGER
#                 )''')



conn = sqlite3.connect('english_bot/databases/main.db')
cursor = conn.cursor()

cursor.execute('SELECT * FROM words')
print(cursor.fetchall())

# cursor.execute("DROP TABLE words")
# cursor.execute('''
#                CREATE TABLE words(
#                id INTEGER PRIMARY KEY,
#                russian_word TEXT,
#                english_word TEXT,
#                creator_id TEXT
#                )''')
