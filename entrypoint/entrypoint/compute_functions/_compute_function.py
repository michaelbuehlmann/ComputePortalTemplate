from typing import Callable, Optional

from pydantic import BaseModel


class ComputeFunctionDefinition(BaseModel):
    slug: str
    name: str
    function: Callable
    globus_uuid: Optional[str] = None
    systems: Optional[list[str]] = None
