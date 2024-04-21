import json
from dataclasses import asdict, dataclass, field
from io import BytesIO
from logging import Logger
from typing import Literal
from icecream import ic
from core.logger import setup_logging
from core.settings import ServiceSettings
from speed.accessor import SpeedReport

REPORT_TYPE = Literal[
    "date_range",
    "week",
    "last_week",
    "month",
    "last_month",
    "day",
]


@dataclass
class Result:
    status: Literal["OK", "ERROR"] = "OK"
    course: str = ""
    result: list = field(default_factory=list)
    message: str = "Успешно"

    def to_dict(self):
        return asdict(self)


async def execute_report(report_service: SpeedReport,
                         report_type: REPORT_TYPE,
                         start_date: str,
                         end_date: str) -> BytesIO:
    if report_type == "date_range":
        return await report_service.get_report(start_date, end_date)
    elif report_type == "last_week":
        return await report_service.get_report_last_week()
    elif report_type == "month":
        return await report_service.get_report_month()
    elif report_type == "last_month":
        return await report_service.get_report_last_month()
    elif report_type == "day":
        return await report_service.get_report_current_day()
    else:
        raise Exception("Неизвестный тип отчёта")


async def execute_rpc_action(report_type: REPORT_TYPE, start_date: str = None, end_date: str = None) -> str:
    logger = setup_logging()
    report_service = SpeedReport(logger)
    try:
        result = Result(course="")
        result.result.append(await execute_report(report_service, report_type, start_date, end_date))

    except Exception as ex:
        return json.dumps(
            Result(
                status="ERROR",
                course="course_type",
                result=[],
                message=str(ex.args[0]),
            ).to_dict()
        )
    return json.dumps(result.to_dict())
