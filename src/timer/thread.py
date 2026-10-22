from PyQt6.QtCore import QThread, pyqtSignal
import time


class TimerThread(QThread):
    tick = pyqtSignal(int)
    finished = pyqtSignal()

    def __init__(self, total_seconds):
        super().__init__()
        self.seconds_left = total_seconds
        self.is_running = True

    def run(self):
        while self.seconds_left > 0 and self.is_running:
            self.tick.emit(self.seconds_left)
            self.seconds_left -= 1
            time.sleep(1)

            if not self.is_running or self.seconds_left == 0:
                self.tick.emit(0)
                self.finished.emit()

    def stop(self):
        self.is_running = False
        