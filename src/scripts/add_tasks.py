import sqlite3
from ..fill_db import DB_PATH
from .custom_messagebox import show_custom_message


def add_items(parent, user_id):
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        try:
            n = cur.execute('SELECT task FROM tasks WHERE user = ?', (user_id,))
            tasks = [row[0] for row in n.fetchall()]
        except Exception:
            show_custom_message(parent, "Ошибка", "Не получилось загрузить задачи,проверьте их наличие")
            
        parent.combo_task.addItems(tasks)
