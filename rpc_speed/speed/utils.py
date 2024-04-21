from datetime import datetime, timedelta
from typing import Tuple


def get_week_number(date_string: str = datetime.now().strftime("%Y-%m-%d")) -> int:
    date = datetime.strptime(date_string, "%Y-%m-%d")
    return date.isocalendar()[1]


def get_start_end_of_week(year: int, week_number: int):
    """
    Get the start and end dates of a specific week in a given year.

    Args:
        year (int): The year for which to get the week.
        week_number (int): The number of the week to retrieve.

    Returns:
        tuple: A tuple containing the start date and end date of the specified week in ISO format (yyyy-mm-dd).
    """
    january_4th = datetime(year, 1, 4)
    january_4th_weekday = january_4th.weekday()
    first_day_of_week_1 = january_4th - timedelta(days=january_4th_weekday)
    start_of_week = first_day_of_week_1 + timedelta(weeks=week_number - 1)
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week.isoformat()[:10], end_of_week.isoformat()[:10]


def get_first_day_of_month(
    date_string: str = datetime.now().strftime("%Y-%m-%d"),
) -> str:
    """
    Get the first day of the month for the given date string.

    Args:
        date_string (str): The date string in the format '%Y-%m-%d'.

    Returns:
        str: The first day of the month in the format '%Y-%m-%d'.
    """
    date = datetime.strptime(date_string, "%Y-%m-%d")
    first_day_raw = date - timedelta(date.day - 1)
    first_day = first_day_raw.isoformat()[:10]
    return first_day


def get_last_day_of_month(
    date_string: str = datetime.now().strftime("%Y-%m-%d"),
) -> str:
    """
    Get the last day of the month for the given date string.

    Args:
        date_string (str): The date string in the format '%Y-%m-%d'.

    Returns:
        str: The last day of the month in the format '%Y-%m-%d'.
    """
    date = datetime.strptime(date_string, "%Y-%m-%d")
    first_day_raw = date - timedelta(date.day - 1)
    last_day_raw = first_day_raw - timedelta(days=1) + timedelta(weeks=4)
    while last_day_raw.month == first_day_raw.month:
        last_day_raw = last_day_raw + timedelta(days=1)
    last_day_raw = last_day_raw - timedelta(days=1)
    last_day = last_day_raw.isoformat()[:10]
    return last_day


def get_first_and_last_day_of_month(
    date_string: str = datetime.now().strftime("%Y-%m-%d"),
) -> Tuple[str, str]:
    """
    Get the first and last day of the month for the given date string.

    Args:
        date_string (str): The date string in the format '%Y-%m-%d'.

    Returns:
        Tuple[str, str]: A tuple containing the first and last day of the month in the format '%Y-%m-%d'.
    """
    first_day = get_first_day_of_month(date_string)
    last_day = get_last_day_of_month(date_string)
    return first_day, last_day
