from .add_tasks import add_items
from ..exceptions.exceptions import InvalidTimeException
from ..fill_db import DB_PATH
import sqlite3


def get_all_values(parent):
    s = parent.sec_value.value()
    m = parent.min_value.value()
    h = parent.hour_value.value()
    
    add_items(parent, parent.user_id)
    parent.task = parent.combo_task.currentText()

    count = parent.combo_task.count()
    items_list = [parent.combo_task.itemText(i) for i in range(count)]
    with sqlite3.connect(DB_PATH) as con:
        cur = con.cursor()
        for ta in items_list:
            cur.execute(
            """
            INSERT INTO tasks(user, task)
            SELECT ?, ?
            WHERE NOT EXISTS (
                SELECT 1 FROM tasks WHERE user = ? AND task = ?
            );
        """,
            (parent.user_id, ta, parent.user_id, ta),
        )

        con.commit()

    parent.seconds_left += s + m * 60 + h * 3600

    if not parent.task:
        raise InvalidTimeException

    