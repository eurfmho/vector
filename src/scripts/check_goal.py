import re
from ..exceptions.exceptions import InvalidTimeException


def get_goal(text) -> list:
    try:
        text = text.lower().strip()
        
        match = re.fullmatch(r'(?:(\d+)h)?\s*(?:(\d+)m)?\s*(?:(\d+)s)?', text)

        if not text or not match:
            raise InvalidTimeException

        h, m, s = (int(x or 0) for x in match.groups())

        if h >= 24 or m >= 60 or s >= 60:
            raise InvalidTimeException

        goal_time = [h, m, s]
        return goal_time
    
    except TypeError:
        raise InvalidTimeException




                