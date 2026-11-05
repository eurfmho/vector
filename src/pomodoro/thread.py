from PyQt6.QtCore import QThread, pyqtSignal
import time


class PomodoroThread(QThread):
    tick = pyqtSignal(int, bool)        
    session_finished = pyqtSignal(bool) 
    finished = pyqtSignal()  
    completed = pyqtSignal()           

    def __init__(self, work_seconds, rest_seconds, amount_sessions):
        super().__init__()
        self.work_seconds = work_seconds
        self.rest_seconds = rest_seconds
        self.amount_sessions = amount_sessions
        self.is_running = True

    def run(self):
        for i in range(self.amount_sessions):
            if not self.is_running:
                break
            
            current_work = self.work_seconds
            while current_work > 0 and self.is_running:
                self.tick.emit(current_work, True)
                time.sleep(1)
                current_work -= 1

            if i + 1 == self.amount_sessions:
                self.is_running = False
                self.finished.emit()
                break
            
            if not self.is_running:
                break
                
            self.session_finished.emit(True)

            current_rest = self.rest_seconds
            while current_rest > 0 and self.is_running:
                self.tick.emit(current_rest, False)
                time.sleep(1)
                current_rest -= 1
                
            if not self.is_running:
                break
                    
            self.session_finished.emit(False)

        if self.is_running:
            self.completed.emit(True)
            self.finished.emit()

    def stop(self):
        self.is_running = False
