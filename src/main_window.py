import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from .pomodoro.pomodoro import PomodoroWindow
from .timer.timer import TimerScreen
from .first_screen_ui import Ui_hihihi
from .stopwatch.stopwatch import StopwatchWindow
from .exceptions.exceptions import InvalidNameException, EmptyNameSpace
from .scripts.custom_messagebox import show_custom_message
from .fill_db import full_fill_bd, DB_PATH
import sqlite3
from .statistics.statistics import load_data


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
    QLineEdit, QSpinBox, QComboBox {
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


class FirstWindow(QMainWindow, Ui_hihihi):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        full_fill_bd()

        self.timer_button.clicked.connect(self.open_timer_window)
        self.stopwatch_button.clicked.connect(self.open_stopwatch_window)
        self.pomodoro_button.clicked.connect(self.open_pomodoro_window)
        self.create_account_btn.clicked.connect(self.create_account)
        self.basic_theme.setChecked(True)
        self.basic_theme.toggled.connect(self.apply_theme)
        self.blue_theme.toggled.connect(self.apply_theme)
        self.generate_btn.clicked.connect(self.beta_load_data)

    def beta_load_data(self):
        try:
            load_data(self, self.current_user)
        except Exception:
            show_custom_message(self, "Ошибка", "Что-то пошло не так,извините")

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
         
    def create_account(self):
        try:
            us = self.username_edit.text()
            
            if not us.strip():  
                raise EmptyNameSpace
            if len(us) >= 10:
                raise InvalidNameException
                
            self.username_edit.setReadOnly(True)
            self.check_account(us)
            
        except InvalidNameException:
            QMessageBox.critical(self, 'Ошибка', 'Имя слишком длинное!')
        except EmptyNameSpace:
            QMessageBox.critical(self, 'Ошибка', 'Сначала введите имя!')

    def apply_theme(self):
        app = QApplication.instance()
        with sqlite3.connect(DB_PATH) as con:
            cur = con.cursor()
            if app:
                if cur.execute('SELECT theme FROM profiles WHERE name = ?', (self.username_edit.text(), )).fetchone()[0][0] == "blue" or self.blue_theme.isChecked():
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = FirstWindow()
    ex.show()
    sys.exit(app.exec())
