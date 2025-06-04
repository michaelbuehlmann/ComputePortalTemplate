import os
from typing import Annotated

from pydantic.functional_validators import AfterValidator
from datasets import Dataset
from datasets import datasets as _datasets

# Only load datasets for this system
_this_system = os.environ.get("HCP_SYSTEM", None)
if _this_system is None:
    raise RuntimeError("HCP_SYSTEM environment variable not set")
_this_system = _this_system.lower()

datasets = {}
for dataset_name, dataset in _datasets.items():
    system = dataset.system
    if system == _this_system:
        datasets[dataset_name] = dataset


def is_dataset(
    dataset: str,
) -> str:
    if dataset not in datasets:
        raise ValueError(f"Dataset {dataset} not found")
    return dataset


DatasetField = Annotated[str, AfterValidator(lambda s: is_dataset(s))]


__all__ = [
    "dataset",
    "Dataset",
    "is_dataset",
    "DatasetField",
]
