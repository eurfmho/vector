import sys
from .thread import TimerThread
from ..exceptions.exceptions import InvalidTimeException
from ..scripts.get_task_widget import Task
from ..scripts.check_goal import get_goal
from ..scripts.now_time import time
from .timer_ui import Ui_timer_screen
from PyQt6.QtWidgets import QDialog,  QLCDNumber, QMessageBox


class TimerScreen(QDialog, Ui_timer_screen):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.start_stop.clicked.connect(self.start_or_stop)
        self.seconds_left = 0
        self.current_seconds = 0 

        self.is_running = True  
        self.is_started = False
        self.timer_thread = None 

    def start_or_stop(self):
        self.is_running = not self.is_running
        if not self.is_started:
            try:
                tt = self.goal.text()
                time_goal = get_goal(tt)
            except InvalidTimeException:
                QMessageBox.critical(self, 'Ошибка', 'Введите цель по образцу: 1h 30m 15s.\n максимум: 24h 59m 59s')
                return None

            seconds_left = sum(x * 60 ** abs(time_goal.index(x) - 2) for x in time_goal)
            task = self.input_task()
            self.task_label.setText(task)

            self.is_started = True
            self.timer_thread = TimerThread(seconds_left)

            self.timer_thread.tick.connect(self.update_label) 
            self.timer_thread.finished.connect(self.on_finished)
            self.timer_thread.start()
            
        else:
            self.timer_thread.stop()
            self.update_label(0)

    def update_label(self, number):
        self.seconds_left = number
        if self.seconds_left == 0:
            self.timer_thread.stop()
            self.on_finished()
        else:
            m = (self.seconds_left // 60) % 60
            self.lcd_min.display(m)
            s = self.seconds_left % 60
            self.lcd_sek.display(s)
            h = s // 3600
            self.lcd_hours.display(h)
        self.now_time.display(time())

    def on_finished(self):
        if self.seconds_left == 0:
            QMessageBox.information(
                self, "Достижение", "Вы дошли до конца, молодцы!")
        else:
            QMessageBox.information(
                self, "Попытка", "Вы попытались, молодцы!")
        #добавить в бд про сессии

    def input_task(self):
        self.task_window = Task(self)
        self.task_window.show()
        task = Task.currentText()
        task_index = Task.currentIndex() #добавить в бд про таски
        sys.exit(self.task_window.exec())
        return task




