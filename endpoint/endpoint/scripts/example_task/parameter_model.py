from typing import List

from pydantic import BaseModel
from endpoint.datasets import DatasetField


class ExampleParameters(BaseModel):
    dataset: DatasetField
    name: str
    option: bool = False

    def to_cmd_args(self) -> List[str]:
        args = [
            "--dataset",
            self.dataset,
            "--name",
            str(self.name),
        ]
        if self.option:
            args.append("--option")

        return args
