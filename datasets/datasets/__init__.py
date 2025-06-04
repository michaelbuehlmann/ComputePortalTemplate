from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from pydantic import BaseModel


class Dataset(BaseModel):
    name: str
    system: str
    required_globus_groups: Optional[list[str]] = None

    # Add other stuff here to work with datasets, such as data paths


datasets: dict[str, Dataset] = {}
# TODO: fix path
_dataset_path = Path(__file__).parent / "dataset_files"

# Loop over all json files in the datasets directory
for _dataset_file in _dataset_path.glob("*.json"):
    with open(_dataset_file) as f:
        _dataset_dict = json.load(f)
    datasets[_dataset_dict["name"]] = Dataset(**_dataset_dict)

__all__ = ["datasets", "Dataset"]
