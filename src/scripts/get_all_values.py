from .task_actions import add_items, save_task
from ..exceptions.exceptions import InvalidTimeException


def get_all_values(parent):
    s = parent.sec_value.value()
    m = parent.min_value.value()
    h = parent.hour_value.value()

    add_items(parent, parent.user_id)
    parent.task = parent.combo_task.currentText()
    parent.combo_task.setEditable(False)

    if not parent.task:
        raise InvalidTimeException

    save_task(parent.user_id, parent.task)

    parent.seconds_left += s + m * 60 + h * 3600
