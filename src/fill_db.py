import sqlite3
import os


DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "vector.db")


def full_fill_bd():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        theme TEXT NOT NULL
    );
    """
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS timer (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user INTEGER NOT NULL,
        status INTEGER,
        time INTEGER NOT NULL,
        task INTEGER NOT NULL,
        FOREIGN KEY (user) REFERENCES profiles(id)
        FOREIGN KEY (task) REFERENCES profiles(tasks)
    );
    """
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS stopwatch (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user INTEGER NOT NULL,
        status INTEGER,
        time INTEGER NOT NULL,
        task INTEGER NOT NULL,
        FOREIGN KEY (user) REFERENCES profiles(id)
        FOREIGN KEY (task) REFERENCES profiles(tasks)
    );
    """
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS pomodoro (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user INTEGER NOT NULL,
        status INTEGER,
        time INTEGER NOT NULL,
        work_time INTEGER NOT NULL,
        rest_time INTEGER NOT NULL,
        amount_of_sessions INTEGER NOT NULL,
        task INTEGER NOT NULL,
        FOREIGN KEY (user) REFERENCES profiles(id)
        FOREIGN KEY (task) REFERENCES profiles(tasks)
    );
    """
    )

    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user INTEGER NOT NULL,
        task TEXT NOT NULL,
        FOREIGN KEY (user) REFERENCES profiles(id)
    );
    """
    )

    conn.commit()
    conn.close()
