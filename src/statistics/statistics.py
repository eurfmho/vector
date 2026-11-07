from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QComboBox, QPushButton, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPdfWriter, QPageLayout, QPageSize, QPainter, QFont

from PyQt6.QtCharts import QChart, QChartView, QPieSeries
import pyqtgraph as pg
from ..fill_db import DB_PATH
import sqlite3


class StatisticsWindow(QWidget):
    def __init__(self, username="Пользователь"):
        super().__init__()
        self.username = username
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        control_layout = QHBoxLayout()
        
        self.period_combo = QComboBox()
        self.period_combo.addItems(["День", "Неделя", "Месяц", "Всё время"])
        self.period_combo.currentIndexChanged.connect(self.update_data)
        
        self.task_combo = QComboBox()
        with sqlite3.connect(DB_PATH) as con:
            cur = con.cursor()
            list_tasks = cur.execute("""
""")
        self.task_combo.addItems(list_tasks)
        self.task_combo.currentIndexChanged.connect(self.update_data)

        control_layout.addWidget(QLabel("Период:"))
        control_layout.addWidget(self.period_combo)
        control_layout.addWidget(QLabel("Дело/Задача:"))
        control_layout.addWidget(self.task_combo)
        
        main_layout.addLayout(control_layout)

        charts_layout = QHBoxLayout()

        self.pie_chart_view = self.create_pie_chart()
        charts_layout.addWidget(self.pie_chart_view)

        self.line_plot_widget = self.create_line_chart()
        charts_layout.addWidget(self.line_plot_widget)

        main_layout.addLayout(charts_layout)

        self.export_btn = QPushButton("Сохранить отчет в PDF")
        self.export_btn.clicked.connect(self.export_to_pdf)
        main_layout.addWidget(self.export_btn)

        self.setLayout(main_layout)

    def create_pie_chart(self):
        series = QPieSeries()
        series.append("Обычные задачи", 120)
        series.append("Секундомер: Цель достигнута", 90)
        series.append("Секундомер: Цель не достигнута", 45)

        chart = QChart()
        chart.addSeries(series)

        chart_view = QChartView(chart)
        return chart_view

    def create_line_chart(self):
        plot_widget = pg.PlotWidget()

        days = [1, 2, 3, 4, 5, 6, 7]
        progress = [15, 30, 25, 40, 55, 50, 65]

        plot_widget.plot(days, progress)
        return plot_widget

    def update_data(self):
        period = self.period_combo.currentText()
        selected_task = self.task_combo.currentText()

    def export_to_pdf(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить отчет", "report.pdf", "PDF Files (*.pdf)")
        if not file_path:
            return

        period = self.period_combo.currentText()

        pie_image = self.pie_chart_view.grab().toImage()
        line_image = self.line_plot_widget.grab().toImage()

        pdf_writer = QPdfWriter(file_path)
        pdf_writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
        pdf_writer.setPageOrientation(QPageLayout.Orientation.Portrait)

        painter = QPainter()
        if not painter.begin(pdf_writer):
            QMessageBox.warning(self, "Ошибка", "Не удалось создать PDF-файл.")
            return

        painter.drawText(100, 200, "Отчет об аналитике времени")
        painter.drawText(100, 300, f"Имя пользователя: {self.username}")
        painter.drawText(100, 350, f"Период аналитики: {period}")

        pie_image_scaled = pie_image.scaled(2000, 1200, Qt.AspectRatioMode.KeepAspectRatio)
        line_image_scaled = line_image.scaled(2000, 1200, Qt.AspectRatioMode.KeepAspectRatio)

        painter.drawImage(100, 450, pie_image_scaled)
        painter.drawImage(100, 1800, line_image_scaled)

        painter.end()
        QMessageBox.information(self, "Успех", f"Отчет успешно сохранен:\n{file_path}")