import time
import sqlite3
from ..fill_db import DB_PATH
from ..scripts.custom_messagebox import show_custom_message
from .thread import PomodoroThread
from ..scripts.now_time import time
from ..scripts.add_tasks import add_items
from .pomodoro_ui import Ui_pomodoro
from ..exceptions.exceptions import InvalidInputData
from PyQt6.QtWidgets import QMainWindow
from datetime import datetime as dt


class PomodoroWindow(QMainWindow, Ui_pomodoro):
    def __init__(self, user_id):
        super().__init__()
        self.setupUi(self)
        self.user_id = user_id
        self.work_on_task_time = 0
        self.rest_time = 0
        self.amount_sessions = 0
        self.task = str()

        self.is_running = False
        self.pomodoro_thread = None
        
        self.start_stop.clicked.connect(self.start_or_stop)

    def start_or_stop(self):
        if not self.is_running:
            try:
                self.get_inserted_time()
            except InvalidInputData:
                show_custom_message(self, 'Ошибка', 'введите корректные данные')     
                return

            seconds_work = self.work_on_task_time * 60
            seconds_rest = self.rest_time * 60

            self.is_running = True
            
            self.pomodoro_thread = PomodoroThread(seconds_work, seconds_rest, self.amount_sessions)
            self.pomodoro_thread.tick.connect(self.update_label)
            self.pomodoro_thread.session_finished.connect(self.handle_session_finished)
            self.pomodoro_thread.finished.connect(self.on_finished)
            self.pomodoro_thread.start()

        else:
            if self.pomodoro_thread:
                self.pomodoro_thread.stop()
                self.pomodoro_thread.wait()
            
            self.is_running = False
            self.start_stop.setText("Старт")
            self.update_label(0, False)
            show_custom_message(self, "Попытка", "Вы попытались, молодцы⭐️️️️")
            with sqlite3.connect(DB_PATH) as con:
                cur = con.cursor()
                cur.execute('''INSERT INTO pomodoro(user, status, work_time, 
                rest_time, amount of sessions, time, date, task) VALUES(?, ?, ?, ?, ?, ?,?, (SELECT id FROM tasks WHERE task = ?))''', (self.user_id, 0, self.work_on_task_time, self.rest_time, self.amount_sessions, self.worked_sekonds, dt.now().strftime("%Y-%m-%d %H:%M:%S"), self.task))
                con.commit()

    def update_label(self, seconds_left, is_work):
        self.worked_sekonds = self.amount_sessions * self.work_on_task_time - seconds_left
        m = (seconds_left // 60) % 60
        s = seconds_left % 60
        self.lcd_min.display(m)
        self.lcd_sek.display(s)
        if is_work:
            self.lb_work_rest.setText("работайте⭐️️️️")
        else:
            self.lb_work_rest.setText("ОТДЫХ⭐️️️️")

        self.lcd_now_time.display(time())

    def handle_session_finished(self, is_work):
        if is_work:
            show_custom_message(self, "Отдых", "Рабочая сессия завершена! Время отдохнуть.⭐️️️️")
        else:
            show_custom_message(self, "Работа", "Отдых окончен! Возвращаемся к работе.⭐️️️️")

    def on_finished(self):
        self.is_running = False
        self.start_stop.setText("Старт")
        show_custom_message(self, "Достижение", "Вы дошли до конца, молодцы!")
        with sqlite3.connect(DB_PATH) as con:
            cur = con.cursor()
            cur.execute('''INSERT INTO pomodoro(user, status, work_time, 
            rest_time, amount_of_sessions, time, date, task) VALUES(?, ?, ?, ?, ?, ?, ?, (SELECT id FROM tasks WHERE task = ?)
            )''', (self.user_id, 1, self.work_on_task_time, self.rest_time, self.amount_sessions, self.work_on_task_time * self.amount_sessions, dt.now().strftime("%Y-%m-%d %H:%M:%S"), self.task))
            con.commit()

    def get_inserted_time(self):
        try:
            add_items(self, self.user_id)
            self.work_on_task_time = self.work_time_wg.value()
            self.rest_time = self.rest_time_wg.value()
            self.amount_sessions = self.amount_of_ssessoins_wg.value()
            self.task = self.combo_task.currentText()
            self.index = self.combo_task.currentIndex()

        except Exception:
            raise InvalidInputData
            
        if not self.work_on_task_time or not self.rest_time or not self.amount_sessions: 
            raise InvalidInputData
        