from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtGui import QPixmap
from pathlib import Path 


path_achivement = Path(__file__).resolve().parent.parent / "images"

def show_custom_message(self, title, text):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(text)

        match title:
            case "Ошибка":
                msg.setIconPixmap(QPixmap(str(path_achivement / "error_icon.jpg")))
            case "Достижение":
                msg.setIconPixmap(QPixmap(str(path_achivement / "achivement_icon.jpg")))
            case "Попытка":
                msg.setIconPixmap(QPixmap(str(path_achivement / "attempt_icon.jpg")))
            case "Отдых":
                msg.setIconPixmap(QPixmap(str(path_achivement / "rest_icon.jpg")))
            case "Работа":
                msg.setIconPixmap(QPixmap(str(path_achivement / "work_icon.jpg")))
            
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #49648d;
            }
            QLabel {
                color: #dae6ef;
            }
            QPushButton {
                color: #dae6ef;
                background-color: #3d5e8f;
                border: 1px solid #6181b1;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #3d5e8f;
            }
        """)
        msg.exec()
