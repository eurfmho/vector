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

def load_data(parent, user_id):
    add_items()
    update_pie_chart(user_id)
    update_line_chart(parent, user_id)

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

def get_filtered_progress_for_task(parent, user_id, task_id) -> list:
    start_date_str = get_date_filter_sql(parent)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = """
        SELECT sub.date, SUM(sub.time) as total_time
        FROM (
            SELECT time, date FROM timer WHERE user = ? AND task = ? AND date >= ?
            UNION ALL
            SELECT time, date FROM stopwatch WHERE user = ? AND task = ? AND date >= ?
            UNION ALL
            SELECT time, date FROM pomodoro WHERE user = ? AND task = ? AND date >= ?
        ) AS sub
        GROUP BY sub.date
        ORDER BY sub.date ASC;
    """
    
    cursor.execute(query, (
        user_id, task_id, start_date_str, 
        user_id, task_id, start_date_str, 
        user_id, task_id, start_date_str
    ))
    rows = cursor.fetchall()
    
    conn.close()
    
    return rows

def update_pie_chart(parent, user_id):         
    parent.pie_series.clear()

    try:
        data = get_time_statistics(user_id)

        for counter_type, duration in data.items():
            if duration:
                parent.pie_series.append(counter_type, duration)

    except Exception:
        show_custom_message(parent, "Ошибка", "Ошибка генераци диаграммы,\nубедитесь,что вы запускали программу")
        return

def update_line_chart(parent, user_id):
    parent.line_series.clear()
    selected_task = parent.combo_task_stat.currentText()
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        task_id = cur.execute('SELEST id FROM tasks WHERE task = ?', (selected_task, ))
    if not selected_task:
        show_custom_message(parent, "Ошибка", "выберите задачу")

    try:
        data = get_filtered_progress_for_task(parent, user_id, task_id)

        parent.line_chart.removeSeries(parent.line_series)
        parent.line_series = QLineSeries()
        parent.line_series.setName(selected_task)

        for day_session, duration in data:
            parent.line_series.append(day_session, duration)

        parent.line_chart.addSeries(parent.line_series)
        parent.line_chart.createDefaultAxes()
        parent.line_chart.setTitle(f"Динамика прогресса: {selected_task}")

    except Exception:
        show_custom_message(parent, "Ошибка", "Произошла ошибка при генерации графика,\nпроверьте наличие сессий приложения")
        return 



con.close()