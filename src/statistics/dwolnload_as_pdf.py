import sqlite3
import traceback
from PyQt6.QtGui import QPainter, QPdfWriter, QPageLayout, QPageSize
from PyQt6.QtCore import Qt, QMarginsF
from PyQt6.QtWidgets import QFileDialog
from ..fill_db import DB_PATH
from ..scripts.custom_messagebox import show_custom_message


def export_to_pdf(parent):
    try:
        with sqlite3.connect(DB_PATH) as con:
            cur = con.cursor()
            row = cur.execute("SELECT name FROM profiles WHERE id = ?", (parent.current_user,)).fetchone()
            username = row[0] if row else "Неизвестно"

        file_path, _ = QFileDialog.getSaveFileName(
            parent, "Сохранить отчет", "vector_report.pdf", "PDF Files (*.pdf)"
        )
        if not file_path:
            return

        pdf_writer = QPdfWriter(file_path)
        pdf_writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        
        page_layout = QPageLayout(
            QPageSize(QPageSize.PageSizeId.A4),
            QPageLayout.Orientation.Portrait,
            QMarginsF(10, 10, 10, 10)  
        )
        pdf_writer.setPageLayout(page_layout)

        painter = QPainter(pdf_writer)
        if not painter.isActive():
            show_custom_message(parent, "Ошибка", "Не удалось инициализировать отрисовку PDF")
            return

        painter.setPen(Qt.GlobalColor.black)
        
        font = painter.font()
        font.setPointSize(16)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(100, 150, "Отчет аналитики приложения «Vector»")

        font.setPointSize(12)
        font.setBold(False)
        painter.setFont(font)
        painter.drawText(100, 340, f"Имя пользователя: {username}")
        painter.drawText(100, 500, f"Период аналитики: {parent.combo_period_stat.currentText()}")

        pie_pixmap = parent.pie_view.grab()
        line_pixmap = parent.line_view.grab()

        painter.drawPixmap(100, 600, 5850, 5550, pie_pixmap)
        painter.drawPixmap(100, 5600, 5850, 8050, line_pixmap)

        painter.end()
        show_custom_message(parent, "Успех", "Отчет успешно сохранен в PDF!")

    except Exception as e:
        traceback.print_exc()
        show_custom_message(parent, "Ошибка", f"Не удалось сохранить PDF: {str(e)}")