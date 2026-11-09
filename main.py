import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, QListWidget, QAbstractItemView
from src.pomodoro.pomodoro import PomodoroWindow
from src.timer.timer import TimerScreen
from src.first_screen_ui import Ui_basic_theme_task
from src.stopwatch.stopwatch import StopwatchWindow
from src.exceptions.exceptions import InvalidNameException, EmptyNameSpace
from src.scripts.custom_messagebox import show_custom_message
from src.fill_db import full_fill_bd, DB_PATH
import sqlite3
from src.statistics.download_file import export_to_txt
from src.scripts.task_actions import show_theme_task
from src.statistics.statistics import load_data, refresh_task_combo, setup_charts
from src.statistics.download_file import export_to_pdf


BLUE_THEME = """
    QMainWindow, QDialog {
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
    }
"""


class FirstWindow(QMainWindow, Ui_basic_theme_task):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        setup_charts(self)
        full_fill_bd()
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

    def main_show_added_items_basic_version():
        show_theme_task(self, self.current_user, self.list_basic_task)

    def main_show_added_items_blue_version():
        show_theme_task(self, self.current_user, self.list_blue_task)
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = FirstWindow()
    ex.show()
    sys.exit(app.exec())
