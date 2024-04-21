import asyncio

from app import MainApp
from core.logger import setup_logging
from rpc.rpc_server import RPCServer
from speed.accessor import SpeedReport
from ya_disk.accessor import YaDiskAccessor


async def run_app():
    logger = setup_logging()
    app = MainApp(YaDiskAccessor, RPCServer, SpeedReport, logger)
    try:
        await app.start()
    except asyncio.CancelledError:
        ...
    finally:
        await app.stop()
