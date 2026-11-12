import sqlite3
from ..fill_db import DB_PATH
from .custom_messagebox import show_custom_message
from PyQt6.QtWidgets import QApplication
from pathlib import Path


def add_items(parent, user_id: int):
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        try:
            n = cur.execute('SELECT task FROM tasks WHERE user = ?', (user_id,))
            tasks = [row[0] for row in n.fetchall()]
        except Exception:
            show_custom_message(parent, "Ошибка", "Не получилось загрузить задачи,проверьте их наличие")
    return tasks
        
def show_added_items(parent, user_id: int, obj):
    tasks = add_items(parent, user_id)
    current = obj.currentText()
    obj.clear()
    obj.addItems(tasks)
    obj.setCurrentText(current)

def check_task_theme(user_id, task):
    app = QApplication.instance()
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        task_theme = str(cur.execute("SELECT theme FROM tasks WHERE user = ? AND task = ?", (user_id, task)).fetchone()[0])
        if task_theme == "blue":
            app.setStyleSheet(BLUE_THEME)
        else:
            app.setStyleSheet('')

  
theme_path = Path(__file__).resolve().parent.parent / "blue_theme.txt"

with open(theme_path, mode="r", encoding="utf-8") as file:
    BLUE_THEME = file.read().strip("\n")
