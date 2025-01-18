from pydantic import BaseModel

from typing import Optional, TypeVar

T = TypeVar("T", bound=BaseModel)


def optional(cls: T) -> T:
    for field in cls.model_fields.values():
        if field.is_required():
            field.default = None
            field.annotation = Optional[field.annotation]

    cls.model_rebuild(force=True)
    return cls
