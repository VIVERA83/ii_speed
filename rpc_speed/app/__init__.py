import asyncio
import json
import logging
from typing import Type

from rpc.rpc_server import RPCServer
from speed.accessor import SpeedReport
from speed.execute_rpc_action import REPORT_TYPE, Result, execute_report
from ya_disk.accessor import YaDiskAccessor


class MainApp:
    def __init__(
        self,
        ya_disk: Type[YaDiskAccessor],
        rpc_server: Type[RPCServer],
        speed_report: Type[SpeedReport],
        logger: logging.Logger = logging.getLogger(__name__),
    ) -> None:
        self.ya_disk = ya_disk(logger=logger)
        self.rpc_server = rpc_server(self.execute_rpc_action, logger)
        self.speed_report = speed_report(logger)
        self.logger = logger

    async def start(self):
        await self.ya_disk.connect()
        await self.rpc_server.connect()
        await self.rpc_server.start()
        self.logger.info(f"{self.__class__.__name__} start.")
        await asyncio.Future()

    async def stop(self):
        await self.ya_disk.disconnect()
        await self.rpc_server.disconnect()
        self.logger.info(f"{self.__class__.__name__} stop.")

    async def execute_rpc_action(
        self, report_type: REPORT_TYPE, start_date: str = None, end_date: str = None
    ):
        try:
            result = Result(course="")
            file = await execute_report(
                self.speed_report, report_type, start_date, end_date
            )
            link = await self.ya_disk.upload_and_get_public_download_link(
                file, file.name
            )
            result.result.append(link)
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
