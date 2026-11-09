from ..scripts.custom_messagebox import show_custom_message
from .thread import TimerThread
from ..exceptions.exceptions import InvalidTimeException
from ..scripts.now_time import time
from .timer_ui import Ui_timer_screen
from PyQt6.QtWidgets import QMainWindow
from PyQt6.QtCore import QEvent
from ..scripts.get_all_values import get_all_values
from ..scripts.task_actions import show_added_items
from ..fill_db import DB_PATH
import sqlite3
from datetime import datetime as dt


class TimerScreen(QMainWindow, Ui_timer_screen):
    def __init__(self, user_id):
        super().__init__()
        self.setupUi(self)
        self.user_id = user_id
        self.start_stop.clicked.connect(self.start_or_stop)
        self.combo_task.installEventFilter(self)
        self.seconds_left = 0
        self.current_seconds = 0  
        self.task = str()

        self.is_ended = False
        self.is_running = True  
        self.is_started = False
        self.timer_thread = None 

    def eventFilter(self, obj, event):
        if obj == self.combo_task and event.type() == QEvent.Type.MouseButtonPress:
            show_added_items(self, self.user_id)
        return super().eventFilter(obj, event)

    def start_or_stop(self):
        self.is_running = not self.is_running
        if not self.is_started:
            self.is_ended = False
            try:
                get_all_values(self)
                self.total_duration = self.seconds_left
            except InvalidTimeException:
                show_custom_message(self, 'Ошибка', 'введите тему сессии')
                return None

            self.is_started = True
            self.timer_thread = TimerThread(self.seconds_left)

            self.timer_thread.tick.connect(self.update_label) 
            self.timer_thread.finished.connect(self.on_finished)
            self.timer_thread.start()
            
        else:
            if self.timer_thread and self.timer_thread.isRunning():
                self.is_ended = True
                self.timer_thread.stop()
                return 
            self.timer_thread.stop()
            self.is_ended = True
            self.update_label(0)

    def update_label(self, number):
        self.seconds_left = number
        if not self.is_ended:
            self.current_seconds = self.total_duration - self.seconds_left
        if self.seconds_left == 0:
            self.lcd_hours.display(0)
            self.lcd_min.display(0)
            self.lcd_sek.display(0)
            self.is_started = False
        else:
            m = (self.seconds_left // 60) % 60
            self.lcd_min.display(m)
            s = self.seconds_left % 60
            self.lcd_sek.display(s)
            h = self.seconds_left // 3600
            self.lcd_hours.display(h)
        self.now_time.display(time())

    def on_finished(self):
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            if not self.is_ended:
                cursor.execute('INSERT INTO timer(user, status, time, date,task) VALUES(?, ?,?, ?,(SELECT id FROM tasks WHERE task = ? AND user = ?))', (self.user_id, 1, self.total_duration, dt.now().strftime("%Y-%m-%d %H:%M:%S"), self.task, self.user_id))
                show_custom_message(
                    self, "Достижение", "Вы дошли до конца, молодцы!")
            else:
                cursor.execute('INSERT INTO timer(user, status, time, date, task) VALUES(?, ?,?, ?, (SELECT id FROM tasks WHERE task = ? AND user = ?))', (self.user_id, 0, self.current_seconds, dt.now().strftime("%Y-%m-%d %H:%M:%S"), self.task, self.user_id))
                show_custom_message(
                    self, "Попытка", "Вы попытались, молодцы!")
            conn.commit()
        self.combo_task.setEditable(True)
