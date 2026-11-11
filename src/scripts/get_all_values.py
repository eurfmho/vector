from .task_actions import add_items
from ..exceptions.exceptions import InvalidTimeException


def get_all_values(parent):
    s = parent.sec_value.value()
    m = parent.min_value.value()
    h = parent.hour_value.value()

    add_items(parent, parent.user_id)
    parent.task = parent.combo_task.currentText()

    if s or m or h:
        raise InvalidTimeException

    if not parent.task:
        raise InvalidTimeException

    parent.seconds_left += s + m * 60 + h * 3600
