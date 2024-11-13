from typing import Dict, Any
from typing import TypeVar, Mapping, Union

T = TypeVar("T", bound=Any)
N = Union[None, T]
Record = Dict[str, T]
RoRecord = Mapping[str, T]

__all__ = ["T", "N", "Record", "RoRecord"]
