from datetime import datetime, timedelta
from io import BytesIO
from logging import Logger, getLogger

from aiohttp import ClientSession
from core.settings import ServiceSettings

from .utils import (
    get_first_and_last_day_of_month,
    get_first_day_of_month,
    get_start_end_of_week,
    get_week_number,
)


class SpeedReport:

    def __init__(
        self,
        logger: Logger = getLogger(__name__),
    ):
        self.logger = logger
        self.settings = ServiceSettings()

    def create_request_url(self, relative_url: str, **parameters) -> str:
        return (
            self.settings.base_url
            + relative_url
            + "?"
            + "&".join([f"{k}={v}" for k, v in parameters.items()])
        )

    @staticmethod
    async def make_request(url: str) -> bytes:
        async with ClientSession() as session, session.get(url) as response:
            return await response.read()

    async def get_report_by_date(self, start_date: str, end_date: str) -> BytesIO:
        """
        Asynchronously retrieves a report for a given date range.

        Args:
            start_date (str): The start date of the report.
            end_date (str): The end date of the report.

        Returns:
            BytesIO: A stream containing the report data.
        """
        url = self.create_request_url(
            self.settings.analysis_report_url, start_date=start_date, end_date=end_date
        )
        response = await self.make_request(url)
        return BytesIO(response)

    async def get_report(
        self, start_date: str, end_date: str, name: str = None, *_, **__
    ) -> BytesIO:
        """
        Async function to get a report within a specific date range and assign a name to the report file.
        Takes in start_date (str), end_date (str), and name (str) as parameters and returns a BytesIO object.

        Args:
            start_date (str): The start date of the report.
            end_date (int): The end date of the report.
            name (str): The name of the report.

        Returns:
            BytesIO: A stream containing the report data.
        """
        file = await self.get_report_by_date(start_date, end_date)
        file.name = name if name else f"report_from {start_date}_to_{end_date}.xlsx"
        return file

    async def get_report_week(self, *_, **__) -> BytesIO:
        """
        Asynchronous function that retrieves a report for the past week and returns it as a BytesIO object.
        No parameters are accepted.

        Returns:
             BytesIO: A BytesIO object containing the report.
        """
        today = datetime.now()
        start = (today - timedelta(6)).strftime("%Y-%m-%d")
        end = today.strftime("%Y-%m-%d")

        return await self.get_report(start, end, f"report_from {start}_to_{end}.xlsx")

    async def get_report_month(self, *_, **__) -> BytesIO:
        """
        Asynchronous function to get the report for the current month.
        It returns a BytesIO object.

        Returns:
            BytesIO: A BytesIO object containing the report.
        """
        today = datetime.now()
        start = (today - timedelta(29)).strftime("%Y-%m-%d")
        end = today.strftime("%Y-%m-%d")

        return await self.get_report(start, end, f"report_from {start}_to_{end}.xlsx")

    async def get_report_current_day(self, *_, **__) -> BytesIO:
        """
        Asynchronously gets the report for the current day.
        Returns a BytesIO object.

        Returns:
            BytesIO: A BytesIO object containing the report.
        """
        start = datetime.now().strftime("%Y-%m-%d")
        return await self.get_report(start, start, f"report_from {start}.xlsx")

    async def get_report_current_week(self, *_, **__) -> BytesIO:
        """
        Asynchronously gets the report for the current week.
        Returns a BytesIO object.

        Returns:
            BytesIO: A BytesIO object containing the report.
        """
        year = datetime.now().year
        week_number = get_week_number()
        start, end = get_start_end_of_week(year, week_number)

        return await self.get_report(start, end, f"report_from {start}_to_{end}.xlsx")

    async def get_report_current_month(self, *_, **__) -> BytesIO:
        """
        Asynchronously gets the report for the current month.
        Returns a BytesIO object.

        Returns:
            BytesIO: A BytesIO object containing the report.
        """
        start, end = get_first_and_last_day_of_month()
        return await self.get_report(start, end, f"report_from {start}_to_{end}.xlsx")

    async def get_report_last_week(self, *_, **__) -> BytesIO:
        """
        Asynchronously gets the report for the last week.
        Returns a BytesIO object.

        Returns:
            BytesIO: A BytesIO object containing the report.
        """
        year = datetime.now().year
        week_number = get_week_number() - 1
        start, end = get_start_end_of_week(year, week_number)

        return await self.get_report(start, end, f"report_from {start}_to_{end}.xlsx")

    async def get_report_last_month(self, *_, **__) -> BytesIO:
        """
        Asynchronously gets the report for the last month.
        Returns a BytesIO object.

        Returns:
            BytesIO: A BytesIO object containing the report.
        """

        first_day = get_first_day_of_month()
        end = (datetime.fromisoformat(first_day) - timedelta(days=1)).isoformat()[:10]
        start = get_first_day_of_month(end)

        return await self.get_report(start, end, f"report_from {start}_to_{end}.xlsx")
