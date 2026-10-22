from ..exceptions.exceptions import InvalidTimeException
from ..scripts.get_task_widget import Task
from ..scripts.check_goal import get_goal
from ..scripts.now_time import time
from .thread import StopwatchThread
from .stopwatch_ui import Ui_stopwatch_screen
from PyQt6.QtWidgets import QMessageBox, QDialog, QLCDNumber, QInputDialog


class StopwatchWindow(QDialog, Ui_stopwatch_screen):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.current_seconds = 0 
        self.goal_sek = 0
        self.is_running = True  
        self.is_started = False
        self.timer_thread = None 
        self.start_stop.clicked.connect(self.start_session)

    def start_session(self):
        self.is_running = not self.is_running
        if not self.is_started:
            try:
                tt = self.goal.text()
                goal = get_goal(tt)
            except InvalidTimeException:
                QMessageBox.critical(self, 'Ошибка', 'Введите цель по образцу: 1h 30m 15s.\n максимум: 24h 59m 59s')
                return None
            self.goal_sek = sum(x * 60 ** abs(goal.index(x) - 2) for x in goal)

            self.is_started = True
            self.watch_thread = StopwatchThread(self.goal_sek)
            task = self.input_task()
            self.task_label.setText(task)

            self.watch_thread.tick.connect(self.update_label)
            self.watch_thread.finished.connect(self.on_finished)
            self.watch_thread.start()
        else:
            self.update_label(0)
            self.watch_thread.stop()

        self.task.setText(self.get_task())

    def update_label(self, number):
        self.current_seconds = number
        m = (self.current_seconds // 60) % 60
        self.lcd_min.display(m)
        s = self.current_seconds % 60
        self.lcd_sek.display(s)
        h = s // 3600
        self.lcd_hours.display(h)

        if self.current_seconds == self.goal_sek:
            QMessageBox.information(
            self, "Достижение", "Вы дошли до конца, молодцы!")
        self.now_time.display(time())
            


    def on_finished(self):
        QMessageBox.information(
            self, "Попытка", "Вы попытались, молодцы!")

        #добавить в бд про сессии

    def get_task(self):
        self.task_window = Task(self, "get_task.ui")
        self.task_window.show()
        task = Task.currentText()
        task_index = Task.currentIndex() #круто добавляем в бд
        return task

    
    