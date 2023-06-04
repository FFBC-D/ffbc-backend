import os
from typing import Generator, TYPE_CHECKING

from pydantic.typing import AnyCallable
from pydantic.validators import str_validator

if TYPE_CHECKING:
    CallableGenerator = Generator[AnyCallable, None, None]

IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg"]
FILE_EXTENSIONS = [".pdf", ".docx", ".svg"]


class ImageExtension(str):
    @classmethod
    def __get_validators__(cls) -> "CallableGenerator":
        yield str_validator
        yield cls.validate

    @classmethod
    def validate(cls, v: str) -> str:
        ext = os.path.splitext(v)[-1].lower()
        if ext not in IMAGE_EXTENSIONS:
            raise ValueError("Invalid image extension")
        return v


class FileExtension(str):
    @classmethod
    def __get_validators__(cls) -> "CallableGenerator":
        yield str_validator
        yield cls.validate

    @classmethod
    def validate(cls, v: str) -> str:
        ext = os.path.splitext(v)[-1].lower()
        if ext not in FILE_EXTENSIONS:
            raise ValueError("Invalid file extension")
        return v
