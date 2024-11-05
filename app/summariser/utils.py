from datetime import datetime, timedelta

import pytz


def parse_time_period(time_period: str, past: bool = True) -> datetime:
    """
    Parses a time period string and returns a datetime object representing the start of the time period
    """

    time_period_hours = int(time_period[:-1])
    if time_period.endswith("h"):
        if past:
            return datetime.now(tz=pytz.UTC) - timedelta(hours=time_period_hours)
        else:
            return datetime.now(tz=pytz.UTC) + timedelta(hours=time_period_hours)
    elif time_period.endswith("d"):
        if past:
            return datetime.now(tz=pytz.UTC) - timedelta(days=time_period_hours)
        else:
            return datetime.now(tz=pytz.UTC) + timedelta(days=time_period_hours)
    else:
        raise ValueError(
            "Invalid time period, should be in hours (h) or days (d), e.g. '24h' or '7d'"
        )
