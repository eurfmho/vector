import sqlite3
from ..fill_db import DB_PATH


def add_items(parent, user_id):
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        
        n = cur.execute('SELECT task FROM tasks WHERE user = ?', (user_id,))
        tasks = [row[0] for row in n.fetchall()]
        
        parent.combo_task.addItems(tasks)
