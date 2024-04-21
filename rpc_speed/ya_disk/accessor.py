import asyncio
import logging
from io import BytesIO
from typing import AsyncGenerator

from yadisk import AsyncClient
from yadisk.exceptions import PathNotFoundError, PathExistsError
from yadisk.objects import AsyncResourceObject, AsyncResourceLinkObject

from core.settings import YaDiskSettings
from .exception import YaFileNotFound, YaTokenNotValidException


class YaDiskAccessor:
    settings: YaDiskSettings
    client: AsyncClient

    def __init__(
            self,
            settings: YaDiskSettings = YaDiskSettings(),
            logger: logging.Logger = logging.getLogger(__name__),
    ) -> None:
        self.settings = settings
        self.logger = logger

    def _check_token(func):  # noqa:
        """A decorator that verifies the Yandex disk token before executing the decorated function.

        Args:
            func (function): The function to be decorated.

        Returns:
            function: The decorated function.
        """

        async def inner(self, *args, **kwargs):
            """
            The inner function that is executed by the decorator.

            Args:
                self (YandexDisk): The YandexDisk instance.
                *args: Variable length argument list.
                **kwargs: Arbitrary keyword arguments.

            Returns:
                object: The return value of the decorated function.
            """
            if await self.client.check_token(self.settings.ya_token):
                return await func(self, *args, **kwargs)
            raise YaTokenNotValidException()

        return inner

    async def connect(self):
        """Connects to the Yandex Disk API using the provided client ID and access token.

        Args:
            self (YandexDisk): The YandexDisk instance.

        Returns:
            None: Returns nothing.
        """
        self.client = AsyncClient(
            id=self.settings.ya_client_id,
            session="aiohttp",
            token=self.settings.ya_token
        )
        await self.__setup()
        self.logger.info(f"{self.__class__.__name__} connected.")

    async def disconnect(self):
        """Disconnects from the Yandex Disk API.

        Args:
            self (YandexDisk): The YandexDisk instance.

        Returns:
            None: Returns nothing.
        """
        await self.client.close()
        self.logger.info(f"{self.__class__.__name__} disconnected.")

    @_check_token  # noqa:
    async def __setup(self):
        """Sets up the Yandex Disk client by verifying the access token and creating the directors if it does not exist.

        Args:
            self (YandexDisk): The YandexDisk instance.

        Returns:
            None: Returns nothing.
        """
        if not await self.client.is_dir(self.settings.ya_base_dir):
            await self.client.mkdir(self.settings.ya_base_dir)

    @_check_token  # noqa:
    async def list_dir(self) -> AsyncGenerator["AsyncResourceObject", None]:
        return await self.client.listdir(self.settings.ya_base_dir)

    def make_file_path(self, upload_file_name: str, number: str = "") -> str:
        """Creates a unique path for the uploaded or otherwise file on Yandex Disk.

        Args:
            upload_file_name (str): The name of the file to be uploaded, or other actions of the file.
            number (str, optional): A number to be appended to the file name to make it unique. Defaults to "".

        Returns:
            str: The unique path for file on Yandex Disk.
        """
        name, *suf = upload_file_name.split(".")
        name += f"({number})" if number else ""
        name += f".{'.'.join(suf)}" if suf else ""
        return "/".join([self.settings.ya_base_dir, name])

    @_check_token  # noqa:
    async def download(self, filename: str) -> BytesIO:
        """
        Downloads a file from Yandex Disk.

        Args:
            filename (str): The name of the file to be downloaded.

        Returns:
            BytesIO: A BytesIO object containing the contents of the file.

        Raises:
            YaFileNotFound: If the file does not exist on Yandex Disk.
        """
        file = BytesIO()
        file.name = filename
        try:
            path_to_file = self.make_file_path(filename)
            await self.client.download(path_to_file, file)
        except PathNotFoundError:
            raise YaFileNotFound(f"File not : {filename}")
        file.seek(0)
        return file

    @_check_token  # noqa:
    async def remove(self, file_name: str):
        """
        Removes a file from Yandex Disk.

        Args:
            file_name (str): The name of the file to be removed.

        Raises:
            YaFileNotFound: If the file does not exist on Yandex Disk.
        """
        path_to_file = self.make_file_path(file_name)
        try:
            return await self.client.remove(path_to_file)
        except PathNotFoundError:
            raise YaFileNotFound(f"File not : {path_to_file}")

    @_check_token  # noqa:
    async def upload(
            self, file: BytesIO | bytes, file_name: str
    ) -> AsyncResourceLinkObject:
        """Uploads a file to Yandex Disk.

        Args:
            file (BytesIO | bytes): The file to be uploaded.
            file_name (str): The name of the file.

        Returns:
            Optional[bool]: Returns True if the file was uploaded successfully, raises an exception otherwise.

        Raises:
            ValueError: If the file could not be uploaded after a certain number of attempts.
            ResourceIsLockedError: If the file is locked on Yandex Disk.
        """
        number = 0
        while number < self.settings.ya_attempt_count:
            upload_file = self.make_file_path(
                f"{file_name}", str(number) if number else ""
            )
            try:
                return await self.client.upload(file, upload_file)
            except PathExistsError:
                self.logger.warning(f"File {upload_file} already exists")
            number += 1
            await asyncio.sleep(1)

        raise ValueError(f"Please rename upload file")

    async def upload_and_get_public_download_link(self, file: BytesIO | bytes, file_name: str) -> str:
        """Uploads a file to Yandex Disk and returns its public download link.

        Args:
            file (BytesIO | bytes): The file to be uploaded.
            file_name (str): The name of the file.

        Returns:
            str: The public download link of the uploaded file.
        """
        ya_object = await self.upload(file, file_name)
        await ya_object.publish()
        return await ya_object.get_download_link()
