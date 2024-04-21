class ExceptionBase(Exception):
    """
    Base class for exceptions.

    Args:
        args (str): The error message.
        exception (Exception): The original exception that caused this exception to be raised.

    Attributes:
        args (str): The error message.
        exception (Exception): The original exception that caused this exception to be raised.
    """

    def __init__(self, *args, exception: Exception = None):
        """
        Initialize the ExceptionBase instance.

        Args:
            args (str): The error message.
            exception (Exception): The original exception that caused this exception to be raised.
        """
        if args:
            self.args = args
        if exception:
            self.exception = exception

    def __str__(self):
        """
        Return the error message.

        Returns:
            str: The error message.
        """
        return f"{self.args[0]}"


class YandexDiskException(ExceptionBase):
    args = ("Unknown error",)


class YaTokenNotValidException(YandexDiskException):
    args = ("The Yandex disk token failed verification, update token.",)


class YaFileNotFound(ExceptionBase):
    args = ("File not found",)
