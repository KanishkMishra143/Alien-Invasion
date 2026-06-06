import sqlite3
import os

DB_FILE = 'game_data.db'

def init_db():
    """Initializes the database and tables if they don't exist."""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS highscore (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                score INTEGER NOT NULL
            );
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS gamestate (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                level INTEGER NOT NULL,
                score INTEGER NOT NULL,
                lives INTEGER NOT NULL
            );
        ''')
        c.execute('SELECT COUNT(*) FROM highscore WHERE id = 1')
        if c.fetchone()[0] == 0:
            c.execute('INSERT INTO highscore (id, score) VALUES (1, 0)')
        conn.commit()

def get_highscore():
    """Gets the high score from the database."""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT score FROM highscore WHERE id = 1')
        result = c.fetchone()
        return result[0] if result else 0

def update_highscore(score: int):
    """Updates the high score if the new score is higher."""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT score FROM highscore WHERE id = 1')
        current_highscore = c.fetchone()[0]
        if score > current_highscore:
            c.execute('UPDATE highscore SET score = ? WHERE id = 1', (score,))
            conn.commit()

def has_saved_game():
    """Checks if a saved game state exists."""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT COUNT(*) FROM gamestate WHERE id = 1')
        return c.fetchone()[0] > 0

def save_gamestate(level: int, score: int, lives: int):
    """Saves the current game state."""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('''
            INSERT OR REPLACE INTO gamestate (id, level, score, lives)
            VALUES (1, ?, ?, ?)
        ''', (level, score, lives))
        conn.commit()

def load_gamestate():
    """Loads the game state from the database."""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('SELECT level, score, lives FROM gamestate WHERE id = 1')
        return c.fetchone()

def delete_gamestate():
    """Deletes the saved game state."""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute('DELETE FROM gamestate WHERE id = 1')
        conn.commit()
