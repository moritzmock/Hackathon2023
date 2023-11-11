import os.path

import dash
from dash import html
from dash import dcc
from dash import Input, Output
import re
import pandas as pd
import plotly.graph_objs as go
import plotly.express as px
import geopandas as gpd
import sys
import time
from plotly.subplots import make_subplots
import numpy as np
import zipfile

# pipiline core
from sklearn.model_selection import GridSearchCV

from pypots.data import load_specific_dataset
from pypots.imputation import SAITS, Transformer

from plotly.subplots import make_subplots



app = dash.Dash()

app.layout = html.Div(children=[
    html.H1(children="Plots per field"),
    dcc.Input(id="field-value", value="P_.49_823"),
    html.Div(children=[
        dcc.Graph(id="plot_1", style={'display': 'inline-block'}),
        dcc.Graph(id="plot_2", style={'display': 'inline-block'})
    ]),
    html.Div(children=[
        dcc.Graph(id="plot_3", style={'display': 'inline-block'}),
        dcc.Graph(id="plot_4", style={'display': 'inline-block'})
    ])
])


def get_df(set_field):
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
    df = df.rename(columns={"#": "date"})
    return df


@app.callback(
    Output(component_id="plot_1", component_property="figure"),
    Input(component_id="field-value", component_property="value")
)
def update(set_field):
    print(set_field)
    df = get_df(set_field)

    # fig = make_subplots(rows=2, cols=2)

    # fig.add_trace(
    #     go.Scatter(
    #         name='Measurement',
    #         x=df['date'],
    #         y=df['tmean'],
    #         mode='lines',
    #         line=dict(color='rgb(31, 119, 180)'),
    #         xaxis="xaxis"
    #     ),
    #     row=1, col=1
    # )

    # fig.add_trace(
    #     go.Scatter(
    #         name='Upper Bound',
    #         x=df['date'],
    #         y=df['tmean'] + df['tmax'],
    #         mode='lines',
    #         marker=dict(color="#444"),
    #         line=dict(width=0),
    #         showlegend=False,
    #         xaxis="xaxis2"
    #     ),
    #     row=1, col=2
    # )

    # fig.add_trace(
    #     go.Scatter(
    #         name='Lower Bound',
    #         x=df['date'],
    #         y=df['tmean'] - df['tmin'],
    #         marker=dict(color="#444"),
    #         line=dict(width=0),
    #         mode='lines',
    #         fillcolor='rgba(68, 68, 68, 0.3)',
    #         fill='tonexty',
    #         showlegend=False
    #     ),
    #     row=2, col=1
    # )




    fig = go.Figure([
        go.Scatter(
            name='Measurement',
            x=df['date'],
            y=df['tmean'],
            mode='lines',
            line=dict(color='rgb(31, 119, 180)')
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


@app.callback(
    Output(component_id="plot_2", component_property="figure"),
    Input(component_id="field-value", component_property="value")
)
def update(set_field):
    df = get_df(set_field)
    # Create figure with secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(
        name='Temperature',
        x=df['date'],
        y=df['tmean'],
        mode='lines',
        line=dict(color='rgb(31, 119, 180)'),
    ))
    fig.add_trace(go.Scatter(
        name='Tmax',
        x=df['date'],
        y=df['tmean'] + df['tmax'],
        mode='lines',
        marker=dict(color="#444"),
        line=dict(width=0),
        showlegend=False)
    )
    fig.add_trace(go.Scatter(
        name='Tmin',
        x=df['date'],
        y=df['tmean'] - df['tmin'],
        marker=dict(color="#444"),
        line=dict(width=0),
        mode='lines',
        fillcolor='rgba(68, 68, 68, 0.3)',
        fill='tonexty',
        showlegend=False
    ))
    fig.add_trace(
        go.Bar(x=df['date'], y=df['pmm'], name="precipitation"),
        secondary_y=True,
    )
    fig.update_layout(
        template='ggplot2',
        yaxis_title='Temperature',
        title='Continuous, variable value error bars',
        hovermode="x"
    )

    return fig

@app.callback(
    Output(component_id="plot_3", component_property="figure"),
    Input(component_id="field-value", component_property="value")
)
def update(set_field):
    df = get_df(set_field)
    fig = px.density_heatmap(df, x="ndvi", y="ndwi", marginal_x="box", marginal_y="box")
    fig.update_layout(
        template='ggplot2')
    return fig

@app.callback(
    Output(component_id="plot_4", component_property="figure"),
    Input(component_id="field-value", component_property="value")
)
def update(set_field):
    df = get_df(set_field)

    X = df.drop(['date'], axis=1)
    X = (X.to_numpy()).reshape(-1, X.shape[0], X.shape[1])
    # X_intact, X, missing_mask, indicating_mask = mcar(X, 0.1) # hold out 10% observed values as ground truth
    # X = masked_fill(X, 1 - missing_mask, np.nan)
    dataset = {"X": X}

    # Model training. This is PyPOTS showtime.
    saits = Transformer(n_steps=X.shape[1], n_features=X.shape[2], n_layers=4, d_model=128, d_inner=256, n_heads=4,
                        d_k=64, d_v=64, dropout=0.1, epochs=10)
    # Here I use the whole dataset as the training set because ground truth is not visible to the model, you can also split it into train/val/test sets
    saits.fit(dataset)
    imputation = saits.predict(dataset)  # impute the originally-missing values and artificially-missing values

    inputed_df = pd.DataFrame(imputation['imputation'].reshape(-1, X.shape[2]), columns=df.keys().tolist()[0:-1])
    inputed_df['date'] = df['date']

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(
        name='NDVI',
        x=inputed_df['date'],
        y=inputed_df['ndvi'],
        mode='lines',
        line=dict(color='rgb(31, 119, 180)'),
    ))
    fig.add_trace(go.Scatter(
        name='NDWI',
        x=inputed_df['date'],
        y=inputed_df['ndwi'],
        mode='lines',
        line=dict(color='rgb(90, 200, 70)'),
    ))

    fig.add_trace(go.Scatter(
        name='NDWI_original',
        x=df['date'],
        y=df['ndwi'],
        mode='lines',
        line=dict(color='rgb(90, 200, 270)'),
    ))

    fig.add_trace(go.Scatter(
        name='NDVI_original',
        x=df['date'],
        y=df['ndvi'],
        mode='lines',
        line=dict(color='rgb(31, 119, 010)'),
    ))

    return fig

if __name__ == "__main__":
    if os.path.isfile("../csv.zip") and not os.path.isdir("../csv_dump"):
        with zipfile.ZipFile("../csv.zip", "r") as zip_ref:
            zip_ref.extractall("../")
    app.run(debug=True)
