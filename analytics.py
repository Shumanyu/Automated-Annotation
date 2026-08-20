import time


def log_event(event_name):
    """Append an event to the local analytics log.

    Best-effort: a read-only working directory should not take down an
    analysis run that is otherwise fine.
    """
    try:
        with open("analytics.log", "a", encoding="utf-8") as f:
            f.write(f"{time.asctime()}: {event_name}\n")
    except OSError:
        pass
