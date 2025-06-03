from typing import Callable, Optional

from pydantic import BaseModel


class FlowStageCode(BaseModel):
    code: str
    state: str | None


class FlowStage(BaseModel):
    tag: str
    name: str
    globusStates: list[str]
    startedCode: FlowStageCode | None
    successCodes: list[FlowStageCode] | None
    failCodes: list[FlowStageCode] | None


class FlowDefinition(BaseModel):
    slug: str
    name: str
    subtitle: str
    flow_definition: dict
    input_schema: dict
    flow_stages: list[FlowStage]
    globus_uuid: Optional[str] = None


class ComputeFunctionDefinition(BaseModel):
    slug: str
    name: str
    function: Callable
    globus_uuid: Optional[str] = None
    systems: Optional[list[str]] = None


class ComputeTestInput(BaseModel):
    endpoint_name: str
    function_name: str
    params: dict
