import asyncio
import json
import logging

from aio_pika import Message, connect
from aio_pika.abc import (
    AbstractChannel,
    AbstractConnection,
    AbstractExchange,
    AbstractIncomingMessage,
    AbstractQueue,
)

from core.settings import RabbitMQSettings
from rpc.dc import Response


class RPCServer:
    connection: AbstractConnection
    channel: AbstractChannel
    exchange: AbstractExchange
    queue: AbstractQueue

    def __init__(
        self, action, logger: logging.Logger = logging.getLogger(__name__)
    ) -> None:
        self.settings = RabbitMQSettings()
        self.queue_name = "rpc_queue"
        self.action = action
        self.logger = logger
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._connect())

    async def start(self) -> None:
        self.logger.info(f"{self.__class__.__name__} start.")
        try:
            async with self.queue.iterator() as queue_iterator:
                message: AbstractIncomingMessage

                async for message in queue_iterator:

                    async with message.process(requeue=False):
                        try:
                            assert message.reply_to is not None, f"Bad message {message}"
                            response = await self._execute_action(message.body)
                        except Exception as e:
                            self.logger.exception("Processing error")
                            response = Response(status="ERROR", message=str(e))
                            await self._reply_to(message, response.to_bytes())
                            continue
                        await self._reply_to(message, str(response).encode("utf-8"))

        except asyncio.CancelledError:
            pass
        finally:
            await self.connection.close()
        self.logger.info(f"{self.__class__.__name__} stop.")

    async def _reply_to(
        self, message: AbstractIncomingMessage, response: bytes
    ) -> None:
        await self.exchange.publish(
            Message(
                body=response,
                correlation_id=message.correlation_id,
            ),
            routing_key=message.reply_to,
        )
        self.logger.debug(f" [x] Sent {response!r}")

    async def _connect(self) -> "RPCServer":
        self.connection = await connect(self.settings.dsn(True))
        self.channel = await self.connection.channel()
        self.exchange = self.channel.default_exchange
        self.queue = await self.channel.declare_queue(self.queue_name)
        return self

    async def _execute_action(self, params: bytes) -> bytes:
        data = json.loads(params.decode("utf-8"))
        return await self.action(**data)
