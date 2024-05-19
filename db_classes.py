import sqlite3


class DB():
    def __init__(self, path: str) -> None:
        self.conn = sqlite3.connect(f'english_bot/databases/{path}.db')
        self.cursor = self.conn.cursor()


    def __del__(self) -> None:
            self.conn.commit()
            self.conn.close()


    #создание нового пользователя
    def create_new_user(self, user_id):
        self.cursor.execute(f'SELECT * FROM user WHERE user_id = {user_id}')
        result = self.cursor.fetchone()
        if result:
            pass
        else:
            self.cursor.execute('INSERT INTO user (user_id, started_word, guessed_word) VALUES (?, ?, ?)', (user_id, 0, 0))


    #учение слов
    def get_random_word_and_translations(self):
        # Выбираем случайное слово из базы данных
        self.cursor.execute('SELECT russian_word, english_word FROM words ORDER BY RANDOM() LIMIT 1')
        word, correct_translation = self.cursor.fetchone()

        # Получаем неверные переводы для этого слова (в данном случае выбираем только 3 неверных перевода)
        self.cursor.execute('SELECT english_word FROM words WHERE russian_word != ? ORDER BY RANDOM() LIMIT 3', (word,))
        wrong_translations = [row[0] for row in self.cursor.fetchall()]

        return word, correct_translation, wrong_translations


    #функционал для добавления слова
    def check_word(self, word):
        self.cursor.execute(f'SELECT COUNT(*) FROM words WHERE russian_word = ?', word)
        return self.cursor.fetchone()
    
    def add_word(self, word, translated_word, user_id):
        self.cursor.execute('INSERT INTO words (russian_word, english_word, creator_id) VALUES (?, ?, ?)', (word, translated_word, user_id))


    #всё что связанно со статистикой
    def correct_answer(self, user_id):
        self.cursor.execute(f'SELECT started_word, guessed_word FROM user WHERE user_id = {user_id}')
        result = cursor.fetchall()[0]
        started_word = result[0] + 1
        guessed_word = result[1] + 1
        self.cursor.execute(f'UPDATE user SET started_word = ?, guessed_word = ? WHERE user_id = {user_id}', (started_word, guessed_word))

    def incorrect_answer(self, user_id):
        self.cursor.execute(f'SELECT started_word FROM user WHERE user_id = {user_id}')
        result = cursor.fetchall()[0][0] + 1
        self.cursor.execute(f'UPDATE user SET started_word = ? WHERE user_id = {user_id}', (result))





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

i = 1108204259
cursor.execute(f'SELECT started_word, guessed_word FROM user WHERE user_id = {i}')
result = cursor.fetchall()[0]
sw = result[0] + 1
gw = result[1] + 1
print(sw, gw)

# cursor.execute('SELECT * FROM words')
# print(cursor.fetchall())

# cursor.execute("DROP TABLE words")
# cursor.execute('''
#                CREATE TABLE words(
#                id INTEGER PRIMARY KEY,
#                russian_word TEXT,
#                english_word TEXT,
#                creator_id TEXT
#                )''')
