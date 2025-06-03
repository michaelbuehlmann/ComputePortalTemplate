from typing import Protocol

from ..models import FlowDefinition
from .compute_with_check_flow import compute_with_check_flow_builder


class FlowBuilder(Protocol):
    def __call__(
        self, setup_function_uuid: str, setup_endpoint_uuid: str
    ) -> FlowDefinition: ...


flow_builders: list[FlowBuilder] = [compute_with_check_flow_builder]
