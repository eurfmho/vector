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
            
        current = parent.combo_task.currentText()
        parent.combo_task.clear()
        parent.combo_task.addItems(tasks)
        parent.combo_task.setCurrentText(current)


def save_task(user_id, task):
    with sqlite3.connect(DB_PATH) as con:
        con.execute(
            """
            INSERT INTO tasks(user, task)
            SELECT ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM tasks WHERE user = ? AND task = ?
            );
            """,
            (user_id, task, user_id, task),
        )

