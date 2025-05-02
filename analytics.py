import time

def log_event(event_name):
    with open("analytics.log", "a") as f:
        f.write(f"{time.asctime()}: {event_name}\n")