import json
from dataclasses import dataclass, field, asdict
from typing import Literal


@dataclass
class Response:
    status: Literal["OK", "ERROR"] = "OK"
    message: str = "Успешно"
    result: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_bytes(self) -> bytes:
        return json.dumps(self.to_dict()).encode("utf-8")
