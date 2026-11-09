import sqlite3
from ..fill_db import DB_PATH
from datetime import datetime, timedelta
from ..scripts.custom_messagebox import show_custom_message
from PyQt6.QtWidgets import QVBoxLayout
from PyQt6.QtCore import Qt, QDateTime
from PyQt6.QtCharts import QChart, QChartView, QPieSeries, QLineSeries, QDateTimeAxis, QValueAxis, QCategoryAxis


def setup_charts(parent):
    parent.pie_series = QPieSeries()
    parent.pie_chart = QChart()
    parent.pie_chart.addSeries(parent.pie_series)
    parent.pie_chart.setTitle("Время по типам счётчиков")
    parent.pie_view = QChartView(parent.pie_chart)
    QVBoxLayout(parent.tab_pie).addWidget(parent.pie_view)

    parent.line_series = QLineSeries()
    parent.line_series.setPointsVisible(True)
    parent.line_chart = QChart()
    parent.line_chart.addSeries(parent.line_series)
    parent.line_axis_x = QDateTimeAxis()
    parent.line_axis_x.setFormat("dd.MM")
    parent.line_axis_y = QValueAxis()
    parent.line_axis_y.setTitleText("секунды")
    parent.line_chart.addAxis(parent.line_axis_x, Qt.AlignmentFlag.AlignBottom)
    parent.line_chart.addAxis(parent.line_axis_y, Qt.AlignmentFlag.AlignLeft)
    parent.line_series.attachAxis(parent.line_axis_x)
    parent.line_series.attachAxis(parent.line_axis_y)
    parent.line_view = QChartView(parent.line_chart)
    QVBoxLayout(parent.tab_line).addWidget(parent.line_view)


def get_date_filter_sql(parent):
    period = parent.combo_period_stat.currentText()
    now = datetime.now()
    if period == "day":
        start_date = now - timedelta(days=1)
    elif period == "week":
        start_date = now - timedelta(weeks=1)
    elif period == "month":
        start_date = now - timedelta(days=30)
    else:
        start_date = datetime(2000, 1, 1)
    return start_date.strftime("%Y-%m-%d %H:%M:%S")


def refresh_task_combo(parent, user_id):
    selected_task = parent.combo_task_stat.currentText()
    with sqlite3.connect(DB_PATH) as con:
        rows = con.execute('SELECT task FROM tasks WHERE user = ?', (user_id, )).fetchall()
    parent.combo_task_stat.clear()
    parent.combo_task_stat.addItems([row[0] for row in rows])
    parent.combo_task_stat.setCurrentText(selected_task)


def load_data(parent, user_id):
    refresh_task_combo(parent, user_id)
    update_pie_chart(parent, user_id)
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
        SELECT DATE(sub.date) AS day, SUM(sub.time) as total_time
        FROM (
            SELECT time, date FROM timer WHERE user = ? AND task = ? AND date >= ?
            UNION ALL
            SELECT time, date FROM stopwatch WHERE user = ? AND task = ? AND date >= ?
            UNION ALL
            SELECT time, date FROM pomodoro WHERE user = ? AND task = ? AND date >= ?
        ) AS sub
        GROUP BY day
        ORDER BY day ASC;
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
        parent.pie_series.setLabelsVisible(True)

    except Exception:
        show_custom_message(parent, "Ошибка", "Ошибка генераци диаграммы,\nубедитесь,что вы запускали программу")
        return


def update_line_chart(parent, user_id):
    parent.line_series.clear()
    selected_task = parent.combo_task_stat.currentText()
    if not selected_task:
        show_custom_message(parent, "Ошибка", "выберите задачу")
        return

    try:
        with sqlite3.connect(DB_PATH) as con:
            task_id = con.execute('SELECT id FROM tasks WHERE task = ? AND user = ?', (selected_task, user_id)).fetchone()[0]
        data = get_filtered_progress_for_task(parent, user_id, task_id)

        points = [(QDateTime.fromString(day, "yyyy-MM-dd"), duration) for day, duration in data]
        for moment, duration in points:
            parent.line_series.append(moment.toMSecsSinceEpoch(), duration)

        parent.line_series.setName(selected_task)
        parent.line_chart.setTitle(f"Динамика прогресса: {selected_task}")
        if points:
            start, end = points[0][0].addDays(-1), points[-1][0].addDays(1)
            parent.line_axis_x.setRange(start, end)
            parent.line_axis_x.setTickCount(min(start.daysTo(end) + 1, 8))
            parent.line_axis_y.setRange(0, max(duration for _, duration in points) * 1.1)

    except Exception:
        show_custom_message(parent, "Ошибка", "Произошла ошибка при генерации графика,\nпроверьте наличие сессий приложения")
        return
