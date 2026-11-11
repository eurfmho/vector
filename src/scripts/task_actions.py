import sqlite3
from ..fill_db import DB_PATH
from .custom_messagebox import show_custom_message
from PyQt6.QtWidgets import QApplication, QInputDialog
from PyQt6.QtCore import QEvent, QObject



def add_items(parent, user_id: int):
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        try:
            n = cur.execute('SELECT task FROM tasks WHERE user = ?', (user_id,))
            tasks = [row[0] for row in n.fetchall()]
        except Exception:
            show_custom_message(parent, "Ошибка", "Не получилось загрузить задачи,проверьте их наличие")
    return tasks
        
def show_added_items(parent, user_id: int):
    tasks = add_items(parent, user_id)
    current = parent.combo_task.currentText()
    parent.combo_task.clear()
    parent.combo_task.addItems(tasks)
    parent.combo_task.setCurrentText(current)

def save_task(user_id: int, task: list):
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

def show_existed_items(parent, user_id, obj):
    tasks = add_items(parent, user_id)
    current = obj.currentText()
    obj.clear()
    obj.addItems(tasks)
    obj.setCurrentText(current)

def check_task_theme(parent, user_id, task):
    app = QApplication.instance()
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        task_theme = str(cur.execute("SELECT theme FROM tasks WHERE user = ? AND task = ?", (user_id, task)).fetchone())
        if task_theme == "blue":
            app.setStyleSheet(BLUE_THEME)
        else:
            app.setStyleSheet()

def delete_task(parent, task):
    pass

BLUE_THEME = """QMainWindow, QDialog {
        background-color: #49648d;
    }
    QLabel {
        color: #dae6ef;
    }
    QRadioButton {
        color: #7998cc;
    }
    QPushButton {
        color: #dae6ef;
        background-color: #3d5e8f;
        border: 1px solid #6181b1;
        border-radius: 4px;
        padding: 5px;
    }
    QPushButton:hover {
        background-color: #3d5e8f;
    }
    QMessageBox {
        background-color: #3d5e8f;
        color: #dae6ef;
    }
    QLineEdit, QSpinBox, QComboBox, QListWidget {
        color: #b5cee1;
        background-color: #3d5e8f;
        border: 1px solid #6181b1;
        border-radius: 3px;
        padding: 2px;
    }
    QLCDNumber {
        color: #93b4cc;
        background-color: #3d5e8f;
        border: 1px solid #6181b1;
    }"""