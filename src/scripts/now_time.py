from datetime import datetime as dt


def time():
    time = dt.now()
    return time.strftime("%H:%M:%S")