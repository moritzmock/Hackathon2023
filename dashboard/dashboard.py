import os.path

import dash
from dash import html
from dash import dcc
from dash import Input, Output
import re
import pandas as pd
import plotly.graph_objs as go
import geopandas as gpd
import sys
import time

sys.path.append("..")
from utils import get_time_series_data_from_polygon




app = dash.Dash()

app.layout = html.Div(children=[
    html.H1(children="Plots per field"),
    dcc.Input(id="field-value"),
    dcc.Graph(id="plot_1")

])


@app.callback(
    Output(component_id="plot_1", component_property="figure"),
    Input(component_id="field-value", component_property="value")
)
def update(set_field):
    set_field = re.sub("\s", "_", set_field)
    set_field = re.sub("/", "-", set_field)
    path = "../csv_dump/{}.csv".format(set_field)

    # nothing was found, two scenarios apply:
    # 1. the user did not yet finish typing
    # 2. the cell is not there
    if not os.path.exists(path):
        return None

    df = pd.read_csv(path)
    df = df.rename(columns={"Unnamed: 0": "date"})

    fig = go.Figure([
        go.Scatter(
            name='Measurement',
            x=df['date'],
            y=df['tmean'],
            mode='lines',
            line=dict(color='rgb(31, 119, 180)'),
        ),
        go.Scatter(
            name='Upper Bound',
            x=df['date'],
            y=df['tmean'] + df['tmax'],
            mode='lines',
            marker=dict(color="#444"),
            line=dict(width=0),
            showlegend=False
        ),
        go.Scatter(
            name='Lower Bound',
            x=df['date'],
            y=df['tmean'] - df['tmin'],
            marker=dict(color="#444"),
            line=dict(width=0),
            mode='lines',
            fillcolor='rgba(68, 68, 68, 0.3)',
            fill='tonexty',
            showlegend=False
        )
    ])
    fig.update_layout(
        yaxis_title='Temperature',
        title='Continuous, variable value min max',
        hovermode="x"
    )

    return fig


if __name__ == "__main__":
    app.run(debug=True)
