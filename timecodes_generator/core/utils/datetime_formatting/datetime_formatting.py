SECONDS_IN_MINUTE = 60
SECONDS_IN_HOUR = SECONDS_IN_MINUTE * 60


def format_timestamp_from_seconds(seconds: int):
    hours = seconds // SECONDS_IN_HOUR

    minutes_remainder = seconds % SECONDS_IN_HOUR // SECONDS_IN_MINUTE
    minutes = (
        minutes_remainder
        if seconds >= SECONDS_IN_HOUR
        else seconds // SECONDS_IN_MINUTE
    )

    seconds_remainder = seconds % SECONDS_IN_MINUTE
    seconds = seconds_remainder if seconds >= SECONDS_IN_MINUTE else seconds

    return f"{hours:02.0f}:{minutes:02.0f}:{seconds:02.0f}"
