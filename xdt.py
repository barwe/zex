from datetime import timezone
from datetime import datetime as DateTime
from typing import Optional


def strfnow(format: Optional[str] = None):
    if format is None:
        format = "%Y%m%d_%H%M%S"
    return DateTime.now().strftime(format)


def seconds_to_iso8601(seconds: int):
    """将秒时间戳转换为 ISO-8601 格式"""
    return DateTime.fromtimestamp(seconds / 1000).replace(tzinfo=timezone.utc).isoformat()


def milliseconds_to_iso8601(milliseconds: int):
    """将毫秒时间戳转换为 ISO-8601 格式"""
    return seconds_to_iso8601(int(milliseconds / 1000))


def milliseconds_to_datetime(milliseconds: int):
    return DateTime.fromtimestamp(milliseconds / 1000)


def str_to_milliseconds(s: str, fmt: str):
    dt = DateTime.strptime(s, fmt)
    utc_time = dt.astimezone(timezone.utc)
    return int(utc_time.timestamp() * 1000)


def datetime_to_milliseconds(dt: Optional[DateTime]):
    if isinstance(dt, DateTime):
        return int(dt.timestamp() * 1000)
    return None


def convert_to_milliseconds(date_string, date_format):
    dt = DateTime.strptime(date_string, date_format)
    timestamp = dt.timestamp()
    milliseconds = int(timestamp * 1000)
    return milliseconds
