import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from .pomodoro.pomodoro import PomodoroWindow
from .timer.__init__ import TimerScreen
from .first_screen import Ui_hihihi
from .stopwatch.stopwatch import StopwatchWindow
from PyQt6.QtGui import QFont


class FirstWindow(QMainWindow, Ui_hihihi):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        print("ПРивет")
        menu_bar = self.menuBar()
        menu_bar.setNativeMenuBar(False)
        font = QFont("Arial", 40)  
        font.setItalic(True)
        menu_bar.setFont(font)
        timer_action = menu_bar.addAction("Timer")
        stopwatch_action = menu_bar.addAction("Stopwatch")
        pomodoro_action = menu_bar.addAction("Pomodoro")
        account_action = menu_bar.addAction("Account")


        timer_action.triggered.connect(self.open_timer_window)
        stopwatch_action.triggered.connect(self.open_stopwatch_window)
        pomodoro_action.triggered.connect(self.open_pomodoro_window)

    def open_timer_window(self):
        self.timer_window = TimerScreen()
        self.timer_window.show()

    def open_stopwatch_window(self):
        self.open_stopwatch_window = StopwatchWindow()
        self.open_stopwatch_window.show()

    def open_pomodoro_window(self):
        self.open_pomodoro_window = PomodoroWindow()
        self.open_pomodoro_window.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = FirstWindow()
    ex.show()
    sys.exit(app.exec())
