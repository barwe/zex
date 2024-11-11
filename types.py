from typing import Dict, Any
from typing import TypeVar, Mapping, Union

T = TypeVar("T")
N = Union[None, T]
Record = Dict[str, Any]
RoRecord = Mapping[str, Any]

__all__ = ["T", "N", "record", "RoRecord"]
