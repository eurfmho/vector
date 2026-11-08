import sqlite3
from ..fill_db import DB_PATH
import datetime as dt
from datetime import datetime, timedelta
from ..scripts.custom_messagebox import show_custom_message
from ..scripts.add_tasks import add_items
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QComboBox, QMessageBox, QFileDialog
)
from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QPdfWriter, QPageLayout, QPageSize
from PyQt6.QtCharts import (
    QChart, QChartView, QPieSeries, QLineSeries, 
    QDateTimeAxis, QValueAxis, QCategoryAxis
)


con = sqlite3.connect(DB_PATH)

def get_date_filter_sql(parent):
    period = parent.combo_period_stat.currentText()
    now = dt.now()
    if period == "День":
        start_date = now - timedelta(days=1)
    elif period == "Неделя":
        start_date = now - timedelta(weeks=1)
    elif period == "Месяц":
        start_date = now - timedelta(days=30)
    else:
        start_date = datetime(2000, 1, 1)
    return start_date.strftime("%Y-%m-%d %H:%M:%S")

def load_data(self, user_id):
    add_items()
    update_pie_chart(user_id)
    update_line_chart()

import sqlite3

def get_time_statistics(user_id):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    stats = {}

    cursor.execute("""
        SELECT status, SUM(time) 
        FROM stopwatch 
        WHERE user = ? 
        GROUP BY status
    """, (user_id,))
    for row in cursor.fetchall():
        status, total_time = row
        label = "stopwatch_achieved" if status == 1 else "stop_watch_failed"
        stats[label] = total_time or 0

    cursor.execute("""
        SELECT SUM(time) 
        FROM timer 
        WHERE user = ?
    """, (user_id,))
    timer_result = cursor.fetchone()[0]
    stats["timer"] = timer_result or 0

    cursor.execute("""
        SELECT SUM(time) 
        FROM pomodoro 
        WHERE user = ?
    """, (user_id,))
    pomodoro_result = cursor.fetchone()[0]
    stats["pomodoro"] = pomodoro_result or 0

    conn.close()
    return stats

def update_pie_chart(parent, user_id):
    parent.pie_series.clear()
    start_date = get_date_filter_sql()

    try:
        data = get_time_statistics(user_id)

        for counter_type, duration in data.items():
            if duration:
                parent.pie_series.append(counter_type, duration)

    except Exception as e:
        show_custom_message(parent, "Ошибка", "Ошибка генераци диаграммы,\nубедитесь,что вы запускали программу")

def update_line_chart(parent, user_id):
    parent.line_series.clear()
    selected_task = parent.combo_task_stat.currentText()
    if not selected_task:
        show_custom_message(parent, "Ошибка", "выберите задачу")

    start_date = get_date_filter_sql()

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        query = """
            SELECT DATE(timestamp) as session_date, SUM(duration) 
            FROM sessions 
            WHERE user_id = ? AND task_name = ? AND timestamp >= ? 
            GROUP BY session_date 
            ORDER BY session_date ASC
        """
        cursor.execute(query, (parent.user_id, selected_task, start_date))
        data = cursor.fetchall()
        conn.close()

        # Добавляем точки на линейный график (в качестве оси X используем порядковые индексы или даты)
        parent.line_chart.removeSeries(parent.line_series)
        parent.line_series = QLineSeries()
        parent.line_series.setName(selected_task)

        for index, (date_str, duration) in enumerate(data):
            self.line_series.append(index, duration)

        self.line_chart.addSeries(self.line_series)
        self.line_chart.createDefaultAxes()
        self.line_chart.setTitle(f"Динамика прогресса: {selected_task}")

    except Exception as e:
        print(f"Ошибка обновления линейного графика: {e}")




con.close()