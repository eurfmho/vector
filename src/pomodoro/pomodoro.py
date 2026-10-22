import time
from .thread import PomodoroThread
from PyQt6.QtCore import QThread
from ..scripts.get_task_widget import Task
from .pomodoro_ui import Ui_pomodoro_window
from PyQt6.QtWidgets import QDialog, QLCDNumber, QInputDialog, QComboBox, QMessageBox


class PomodoroWindow(QDialog, Ui_pomodoro_window):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.work_on_rask_time = 0
        self.rest_time = 0
        self.amount_sessions = 0

        self.is_running = False.    
        self.is_working = False 
        self.pomodoro_thread = None
        self.start_stop.clicked.connect(self.start_stop_pomodoro)

    def get_inserted_time(self):
        self.work_on_rask_time = self.work_time_wg.value()
        self.rest_time = self.rest_time_wg.value()
        self.amount_sessions = self.amount_of_ssessoins_wg.value()
        
        if not self.work_on_rask_time or not self.rest_time or not self.amount_sessions:
            QMessageBox.critical(self, 'ERROR', 'введите не нулевые значения')
            return None
        
        return None

    def start_or_stop(self):
            self.is_running = not self.is_running
            if not self.is_started:
                self.get_inserted_time()
    
                seconds_left = sum(x * 60 ** abs(time_goal.index(x) - 2) for x in time_goal)
                task = self.input_task()
                self.task_label.setText(task)
    
                self.is_started = True
                self.pomodoro_thread = PomodoroThread(seconds_left)
    
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
                
    def start_stop_pomodoro(self):
        self.is_running = not self.is_running
        if self.is_running:

            
        #каждую секунду обновляется экран и вызывается now_time
        #здесь вызывается геттаск и гетинсертедтайм
        #весь помодоро(возможно)
        #в конце при выволненой цели QMessageBox.information(self, 'Достижение', 'Вы выполнили цель')

    def get_tack(self):
        self.task_window = Task(self)
        self.task_window.show()
        self.task = Task.currentText()
        self.task_index = Task.currentIndex() #круто добавляем в бд