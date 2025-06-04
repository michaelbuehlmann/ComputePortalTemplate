from ...preview_data import PlotData, PreviewData
import plotly.graph_objects as go
import numpy as np
from datetime import datetime


def create_preview_figure(name: str, dataset: str) -> go.Figure:
    fig = go.Figure()
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name="Sine Wave"))
    fig.update_layout(
        title=f"Preview for {name} with dataset {dataset}",
        xaxis_title="X Axis",
        yaxis_title="Y Axis",
        template="plotly_white",
    )
    return fig


def create_preview_data(input_data: dict, output_file: str) -> PreviewData:
    fig = create_preview_figure(input_data["name"], input_data["dataset"])
    plot_data = PlotData(
        plotly_data=fig,
        title=f"Preview for {input_data['name']} with dataset {input_data['dataset']}",
        description=f"This is a preview of the example task with name {input_data['name']} and dataset {input_data['dataset']}.",
    )

    preview_data = PreviewData(
        plots=[plot_data], date=datetime.now(), inputData=input_data
    )

    with open(output_file, "w") as f:
        f.write(preview_data.json(indent=2))

    return preview_data
