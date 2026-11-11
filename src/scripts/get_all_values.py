from .task_actions import show_added_items
from ..exceptions.exceptions import InvalidTimeException


def get_all_values(parent):
    s = parent.sec_value.value()
    m = parent.min_value.value()
    h = parent.hour_value.value()

    parent.task = parent.combo_task.currentText()

    if not parent.task:
        raise InvalidTimeException

    parent.seconds_left += s + m * 60 + h * 3600
