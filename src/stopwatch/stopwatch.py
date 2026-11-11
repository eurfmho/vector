from ..exceptions.exceptions import InvalidTimeException
from ..scripts.now_time import time
from ..scripts.custom_messagebox import show_custom_message
from .thread import StopwatchThread
from .stopwatch_ui import Ui_stopwatch_screen
from PyQt6.QtWidgets import QMainWindow
from ..scripts.get_all_values import get_all_values
from ..fill_db import DB_PATH
import sqlite3
from datetime import datetime as dt
from ..scripts.task_actions import show_added_items

class StopwatchWindow(QMainWindow, Ui_stopwatch_screen):
    def __init__(self, user_id):
        super().__init__()
        self.setupUi(self)
        try:
            self.user_id = user_id
        except:
            show_custom_message(self, "Ошибка", "создайте аккаунт или авторизуйтесь")
        show_added_items(self, self.user_id, self.combo_task)
        self.current_seconds = 0 
        self.seconds_left = 0
        self.task = str()

        self.is_running = True  
        self.is_started = False
        self.timer_thread = None 
        self.combo_task.installEventFilter(self)
        self.start_stop.clicked.connect(self.start_session)

    def start_session(self):
        self.is_running = not self.is_running
        if not self.is_started:
            try:
                show_added_items(self, self.user_id, self.combo_task)
                get_all_values(self)
            except InvalidTimeException:
                show_custom_message(self, 'Ошибка', 'введите тему сессии')
                return None
            
            self.goal_achieved = False
            self.is_started = True
            self.watch_thread = StopwatchThread(self.seconds_left)

            self.watch_thread.tick.connect(self.update_label)
            self.watch_thread.finished.connect(self.on_finished)
            self.watch_thread.start()
        else:
            self.watch_thread.stop()
            self.update_label(0)

    def update_label(self, number):
        self.current_seconds = number
        m = (self.current_seconds // 60) % 60
        self.lcd_min.display(m)
        s = self.current_seconds % 60
        self.lcd_sek.display(s)
        h = self.current_seconds // 3600
        self.lcd_hours.display(h)

        if self.current_seconds == self.seconds_left:
            self.goal_achieved = True
            show_custom_message(
            self, "Достижение", "Вы дошли до конца, молодцы!")
        self.now_time.display(time())

    def on_finished(self):
        self.seconds_left = 0
        self.is_started = False
        if not self.goal_achieved:
            show_custom_message(
                self, "Попытка", "Вы попытались, молодцы!")
        with sqlite3.connect(DB_PATH) as con:
            cursor = con.cursor()
            cursor.execute("INSERT INTO stopwatch(user, status, time, date, task) VALUES(?, ?, ?, ?,(SELECT id FROM tasks WHERE task = ? AND user = ?))", (self.user_id, int(self.goal_achieved), self.watch_thread.current_seconds, dt.now().strftime("%Y-%m-%d %H:%M:%S"), self.task, self.user_id))
            con.commit()
        self.current_seconds = 0
