import sqlite3
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPdfWriter, QPageLayout, QPageSize, QPainter
from ..fill_db import DB_PATH


def get_tasks_from_db(user: int):
    """Получает список всех задач из базы данных."""
    try:
        with sqlite3.connect(DB_PATH) as con:
            cur = con.cursor()
            iter_tasks = cur.execute("SELECT task FROM tasks WHERE id = ?", (user)).fetchall()
            return [row[0] for row in iter_tasks]
    except Exception:
        return []


def fetch_statistics_data(period="День", selected_task=None):
    """Собирает и возвращает статистические данные для отчета."""
    # Здесь можно добавить реальные запросы в БД в зависимости от period и selected_task
    data = {
        "period": period,
        "task": selected_task,
        "normal_tasks": 120,
        "successed": 90,
        "failed": 45,
        "progress_days": [1, 2, 3, 4, 5, 6, 7],
        "progress_values": [15, 30, 25, 40, 55, 50, 65]
    }
    return data


def build_pdf_document(file_path, username="Пользователь", period="День", selected_task=None):
    """Создает и сохраняет PDF-отчет, используя данные из функции fetch_statistics_data."""
    if not file_path:
        return False

    # Получаем данные через другую функцию
    data = fetch_statistics_data(period, selected_task)

    pdf_writer = QPdfWriter(file_path)
    pdf_writer.setPageSize(QPageSize(QPageSize.PageSizeId.A4))
    pdf_writer.setPageOrientation(QPageLayout.Orientation.Portrait)

    painter = QPainter()
    if not painter.begin(pdf_writer):
        return False

    # Записываем данные в документ
    painter.drawText(100, 200, "Отчет об аналитике времени")
    painter.drawText(100, 300, f"Имя пользователя: {username}")
    painter.drawText(100, 350, f"Период аналитики: {period}")
    
    if selected_task:
        painter.drawText(100, 400, f"Выбранная задача: {selected_task}")
    
    painter.drawText(100, 500, f"Обычные задачи: {data['normal_tasks']}")
    painter.drawText(100, 550, f"Цель достигнута: {data['stopwatch_success']}")
    painter.drawText(100, 600, f"Цель не достигнута: {data['stopwatch_fail']}")

    painter.end()
    return True


def generate_statistics_report(file_path, username="Пользователь", period="День", selected_task=None):
    """Главная функция-диспетчер, координирующая процесс получения данных и экспорта."""
    # Шаг 1: Проверяем доступность задач (пример взаимодействия функций)
    tasks = get_tasks_from_db()
    if selected_task and selected_task not in tasks and selected_task != "Все задачи":
        print(f"Внимание: задача '{selected_task}' не найдена в базе.")

    # Шаг 2: Генерируем PDF
    success = build_pdf_document(file_path, username, period, selected_task)
    return success