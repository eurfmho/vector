from PyQt6.QtCore import QThread, pyqtSignal
import time


class StopwatchThread(QThread):
    tick = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, goal_sek):
        super().__init__()
        self.goal_sek = goal_sek
        self.current_seconds = 0
        self.is_running = True

    def run(self):
        while self.is_running:
            self.tick.emit(self.current_seconds)
            self.current_seconds += 1
            time.sleep(1)

            if not self.is_running:
                self.tick.emit(0)
                self.finished.emit()

    def stop(self):
        self.is_running = False
