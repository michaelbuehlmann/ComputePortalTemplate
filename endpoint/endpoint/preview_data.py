import json
from datetime import datetime
from typing import Optional

from plotly.graph_objects import Figure
from pydantic import BaseModel, ConfigDict, PlainSerializer
from typing_extensions import Annotated

# TODO: add actual validation
AnnotatedPlotlyFigure = Annotated[
    Figure,
    PlainSerializer(lambda f: json.loads(f.to_json())),
]


class DownloadLink(BaseModel):
    url: Optional[str]
    filename: str
    description: str


class PlotData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    plotly_data: AnnotatedPlotlyFigure
    title: str
    description: str


class PreviewData(BaseModel):
    plots: list[PlotData]
    date: datetime
    inputData: dict
