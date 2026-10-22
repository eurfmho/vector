from PyQt6.QtWidgets import QDialog 
from .get_task_ui import Ui_get_task

class Task(QDialog, Ui_get_task):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setupUi(self.parent)