from ._compute_function import ComputeFunctionDefinition
from .example import exampletask

compute_functions: list[ComputeFunctionDefinition] = [
    exampletask,
]

__all__ = ["compute_functions"]
