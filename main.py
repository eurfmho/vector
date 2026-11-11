import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QInputDialog
from src.pomodoro.pomodoro import PomodoroWindow
from src.timer.timer import TimerScreen
from src.first_screen_ui import Ui_basic_theme_task
from src.stopwatch.stopwatch import StopwatchWindow
from src.exceptions.exceptions import InvalidNameException, EmptyNameSpace
from src.scripts.custom_messagebox import show_custom_message
from src.fill_db import full_fill_bd, DB_PATH
from PyQt6.QtCore import QEvent, QObject, Qt
import sqlite3
from src.statistics.download_file import export_to_txt
from src.scripts.task_actions import show_added_items, check_task_theme
from src.statistics.statistics import load_data, refresh_task_combo, setup_charts
from src.statistics.download_file import export_to_pdf


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


class FirstWindow(QMainWindow, Ui_basic_theme_task):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        setup_charts(self)
        full_fill_bd()
        self.click_filter = ClickFilter(self)
        self.list_tasks.installEventFilter(self.click_filter)
        self.timer_button.clicked.connect(self.open_timer_window)
        self.stopwatch_button.clicked.connect(self.open_stopwatch_window)
        self.pomodoro_button.clicked.connect(self.open_pomodoro_window)
        self.create_account_btn.clicked.connect(self.create_account)
        self.basic_theme.setChecked(True)
        self.basic_theme.toggled.connect(self.apply_theme)
        self.blue_theme.toggled.connect(self.apply_theme)
        self.generate_btn.clicked.connect(self.beta_load_data)
        self.download_pdf_btn.clicked.connect(self.beta_export_to_pdf)
        self.download_txt_btn.clicked.connect(self.beta_export_to_txt)
        self.apply_theme_task_btn.clicked.connect(self.main_show_added)
        self.apply_theme_task_btn.clicked.connect(self.save_theme_task)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            self.delete_task()
        if event.key() == Qt.Key.Key_1:
            self.tab_3.setCurrentIndex(0)
        if event.key() == Qt.Key.Key_2:
            self.tab_3.setCurrentIndex(1)
        if event.key() == Qt.Key.Key_3:
            self.tab_3.setCurrentIndex(2)

    def add_items(self):
        task, ok = QInputDialog.getText(self, "Новое задание", "Введите название:")
        if ok and task:
            self.list_tasks.addItem(task)

        with sqlite3.connect(DB_PATH) as con:
            cur = con.cursor()
            try:
                cur.execute("""
                                INSERT INTO tasks(user, task)
                                SELECT ?, ?
                                WHERE NOT EXISTS (
                                    SELECT 1 FROM tasks WHERE user = ? AND task = ?
                                );
                                """, (self.current_user, task, self.current_user, task))
                con.commit()
            except Exception:
                show_custom_message(self, "Ошибка", "Войдите в аккаунт или создайте его")

    def delete_task(self):
        task = self.list_tasks.currentItem()
        if not task:
            show_custom_message(self, "Ошибка", "Не пытайтесь удалить пустоту")
            if task:
                row = self.list_tasks.row(task)
                self.list_tasks.takeItem(row)

        with sqlite3.connect(DB_PATH) as con:
            cur = con.cursor()
            cur.execute("DELETE FROM timer WHERE task = ? AND user = ?", (task, self.current_user))
            cur.execute("DELETE FROM pomodoro WHERE task = ? AND user = ?", (task, self.current_user))
            cur.execute("DELETE FROM stopwatch WHERE task = ? AND user = ?", (task, self.current_user))
            cur.execute("DELETE FROM tasks WHERE task = ? AND user = ?", (task, self.current_user))
            con.commit()

    def open_timer_window(self):
        try:
            self.timer_window = TimerScreen(self.current_user)
            self.timer_window.show()
        except Exception:
            show_custom_message(self, 'Ошибка', 'создайте аккаунт или авторизуйтесь')

    def open_stopwatch_window(self):
        try:
            self.stopwatch_window = StopwatchWindow(self.current_user)
            self.stopwatch_window.show()
        except Exception:
            show_custom_message(self, 'Ошибка', 'создайте аккаунт или авторизуйтесь')

    def open_pomodoro_window(self):
        try:
            self.pomodoro_window = PomodoroWindow(self.current_user)
            self.pomodoro_window.show()
        except Exception:
            show_custom_message(self, 'Ошибка', 'создайте аккаунт или авторизуйтесь')

    def beta_export_to_pdf(self):
        export_to_pdf(self)

    def beta_export_to_txt(self):
        export_to_txt(self)

    def beta_load_data(self):
        try:
            load_data(self, self.current_user)
        except Exception:
            show_custom_message(self, "Ошибка", "Что-то пошло не так,извините")

    def save_theme_task(self):
        blue_task = self.combo_blue_task.currentText()
        basic_task = self.combo_basic_task.currentText()

        if blue_task == basic_task:
            show_custom_message(self, "Ошибка", "Выберите разные задания")
            return
        if blue_task == "" or basic_task == "":
            show_custom_message(self, "Ошибка", "Укажите значение перед тем,как сохранять настройки")
            return
        
        with sqlite3.connect(DB_PATH) as con:
            cur = con.cursor()
            cur.execute("UPDATE tasks SET theme = 'blue' WHERE user = ? AND task = ?", (self.current_user, blue_task))
            cur.execute("UPDATE tasks SET theme = 'basic' WHERE user = ? AND task = ?", (self.current_user, basic_task))
            con.commit()
    
    def create_account(self):
        try:
            us = self.username_edit.text()
            
            if not us.strip():  
                raise EmptyNameSpace
            if len(us) >= 10:
                raise InvalidNameException
                
            self.username_edit.setReadOnly(True)
            self.check_account(us)
            refresh_task_combo(self, self.current_user)
            
        except InvalidNameException:
            QMessageBox.critical(self, 'Ошибка', 'Имя слишком длинное!')
        except EmptyNameSpace:
            QMessageBox.critical(self, 'Ошибка', 'Сначала введите имя!')

    def apply_theme(self):
        app = QApplication.instance()
        with sqlite3.connect(DB_PATH) as con:
            cur = con.cursor()
            if app:
                if self.blue_theme.isChecked():
                    app.setStyleSheet(BLUE_THEME)
                    cur.execute("UPDATE profiles SET theme = 'blue' WHERE name = ?", (self.username_edit.text(), ))
                    con.commit()
                else:
                    app.setStyleSheet("")                   
                    cur.execute("UPDATE profiles SET theme = 'basic' WHERE name = ?", (self.username_edit.text(), ))
                    con.commit()
    
    def check_account(self, perhaps_a_name):
        with sqlite3.connect(DB_PATH) as con:
            cursor = con.cursor()
            result = cursor.execute("SELECT name FROM profiles WHERE name = ?", (perhaps_a_name, )).fetchall()
            if not result:
                cursor.execute("INSERT INTO profiles(name, theme) VALUES(?, ?)", (perhaps_a_name, "blue" if self.blue_theme.isChecked() else "basic"))
            else:
                theme_acc = cursor.execute("SELECT theme FROM profiles WHERE name = ?", (perhaps_a_name, ))
                try:
                    if theme_acc.fetchall()[0][0] == "blue":
                        app.setStyleSheet(BLUE_THEME)
                        self.blue_theme.setChecked(True)

                    else:
                        app.setStyleSheet("")
                        self.basic_theme.setChecked(True)
                except Exception:
                    show_custom_message(self, "Ошибка", "создайте аккаунт")
            self.current_user = int(cursor.execute("select id from profiles where name = ?", (perhaps_a_name, )).fetchone()[0])

    def main_show_added(self, blue_or_not: int):
        combo = self.combo_blue_task if blue_or_not else self.combo_basic_task
        show_added_items(self, self.current_user, combo)


class ClickFilter(QObject):
    def __init__(self, window):
        super().__init__()
        self.window = window  

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.MouseButtonPress:
            if obj == self.window.list_tasks:
                self.window.add_items()               

        return super().eventFilter(obj, event)

    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = FirstWindow()
    ex.show()
    sys.exit(app.exec())
