import dash
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dash.dependencies import Output, Input, State
from matplotlib.widgets import Button, Slider
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
import dash_daq as daq
from scipy.spatial import distance
from components import NamedSlider
from figures import *
from nlp_scatter import *
from preprocessing import append_files

# We use the combined dataset in our project for fast slicing by date-indexes.
df = pd.read_csv('Dataset/Complete_sorted_by_date.csv')

card_content = [
    dbc.CardHeader("Question"),
    dbc.CardBody(
        [
            html.H5("Card title", className="card-title", id='card_question'),
            html.H6("Card ", id='card_question_by'),
            html.P(
                "This is some card content that we'll reuse",
                className="card-text", id='card_text'
            ),
        ]
    ),
]

scatter_col = [
    NamedSlider(
        name="Sample Size",
        short="samplesize",
        min=50,
        max=500,
        step=50,
        val=50,
        marks={i: str(i) for i in list(range(50, 550, 50))},
    ),
    NamedSlider(
        name="Perplexity",
        short="perplexity",
        min=5,
        max=50,
        step=10,
        val=35,
        marks={i: str(i) for i in [5, 15, 25, 35, 45, 50]},
    ),
    NamedSlider(
        name="Initial PCA Dimensions",
        short="pca-dimension",
        min=10,
        max=25,
        step=None,
        val=25,
        marks={i: str(i) for i in [10, 15, 20, 25]},
    ),
    daq.ToggleSwitch(
        id='scatter_switch',
        value=False,
        label="Label Points with Question Title"
    ),
]

dropbox_heatmap = html.Div([
    dcc.Dropdown(
        id='heatmap-dropdown',
        options=[
            {'label': 'Ministers vs Ministries', 'value': '1'},
            {'label': 'States Vs Ministries', 'value': '2'},
        ],
        value='1',
        style={'margin-bottom': '10px'})
])


def dash_app():
    app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
    styles = {
        'pre': {
            'border': 'thin lightgrey solid',
            'overflowX': 'scroll'
        }
    }

    app.layout = html.Div([

        html.Div(id="output-clientside"),

        # Header
        html.Div([
            html.Div([
                html.Img(
                    src="assets/logo.png",
                    id="plotly-image",
                    style={
                        "height": "120px",
                        "width": "auto",
                        "display": "block",
                        "margin-left": "auto",
                        "margin-right": "auto"
                    },
                )
            ], className="two columns", style={"align-items": "center", "justify-content": "center"}),

            html.Div([
                html.Div(
                    [
                        html.H3(
                            "Inside Rajya Sabha",
                            style={"margin-bottom": "0px", "text-align": "center"},
                        ),
                        html.H5(
                            "Visualization of Q&A Hour", style={"margin-top": "0px", "text-align": "center"}
                        ),
                    ]
                )
            ], className="eight columns", style={"align-items": "center", "justify-content": "center"}),

            html.Div([
                dbc.Button("Learn More", outline=True, color="dark", className="mr-1"),
            ], className="two columns",
                style={"align-items": "center", "justify-content": "center", "margin-left": "auto",
                       "margin-right": "auto"}),

        ], className="row flex-display pretty_container",
            style={"margin-bottom": "25px", "align-items": "center", "justify-content": "end"}),

        # Year Slider

        html.Div([
            html.Div([
                dcc.RangeSlider(id="year_slider", min=2009, max=2017, value=[2009, 2011], className="dcc_control",
                                allowCross=False, marks={
                        2009: '2009',
                        2010: '2010',
                        2011: '2011',
                        2012: '2012',
                        2013: '2013',
                        2014: '2014',
                        2015: '2015',
                        2016: '2016',
                        2017: '2017'
                    }),
            ], className="pretty_container two-third1 column"),
            html.Div([
                daq.LEDDisplay(
                    id='number_of_rows',
                    color="#1eaedb",
                    backgroundColor='#f9f9f9',
                    value="",
                    size=22,
                )
            ], className="pretty_container one-third1 column",
                style={'text-align': 'center', 'justify-content': 'center', 'font-weight': 'bold', }),
        ], className="row flex-display sticky-top",
            style={'background-color': 'rgba(128,128,128,0.1)', 'backdrop-filter': 'blur(10px)',
                   'box-shadow': '0 4px 8px 0 rgba(0,0,0,0.2)', 'border-radius': '5px'}, ),

        # Graph 1:Total Questions by ministry
        html.Div([
            html.Div([
                dcc.Graph(id='total_questions_by_ministry'),
                html.P("Click on a bar to reveal distribution by ministers",
                       style={'text-align': 'center', 'margin-top': '2px'}),
            ], className="pretty_container twelve columns"),

        ], className="row flex-display"),
        # Graph 2: Total question by ministers
        html.Div([
            html.Div([
                dcc.Graph(id='total_questions_by_ministers'),
                html.P(" ")
            ], className="pretty_container twelve columns"),
        ], className="row flex-display"),
        # Graph 3: Total question by ministry overtime

        html.Div(
            [
                dbc.Row(
                    [
                        dbc.Col(
                            html.Div([
                                html.Div([
                                    dcc.Graph(id='total_questions_overtime'),
                                    html.P("Select a legend to show the distribution", style={'text-align': 'center', })
                                ], className="pretty_container twelve columns"),
                            ], className=""),
                        ),

                        dbc.Col(html.Div([
                            html.Div([
                                dcc.Graph(id='sunburst'),
                                html.P("Select period to reveal a sunburst chart",
                                       style={'text-align': 'center', }),

                            ], className="pretty_container twelve columns"),

                        ], className=""),

                            width=4),
                    ], className="row", no_gutters=True
                ),
            ]
        ),

        # Graph 4: Parallel category chart
        html.Div([
            html.Div([
                dcc.Graph(id='paralle_category_plot_by_party_name')
            ], className="pretty_container twelve columns"),
        ], className="row flex-display", ),
        # Graph 5:  Mapbox
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id='mapbox-dropdown',
                    options=[
                        {'label': 'Total members from states', 'value': 'members'},
                        {'label': 'Total questions from states', 'value': 'questions'},
                    ],
                    value='members',
                    style={'margin-bottom': '10px'}
                ),
                dcc.Graph(id='mapbox', )
            ], className="pretty_container one-half column"),
            html.Div([
                dcc.Graph(id='mapbox-clicked-data'),
                html.P("Click on map to change data", style={'text-align': 'center', })
            ], className="pretty_container one-half column"),

        ], className="row flex-display", ),

        # Graph 6: Heatmaps
        html.Div([
            html.Div([

                dbc.Tabs([
                    dbc.Tab(label="States vs Ministries", children=[

                        dcc.Graph(id='heatmap_state_vs_ministry'),
                        html.P("Select a Box to view the distribution overtime", style={'text-align': 'center', }),
                        dcc.Graph(id='heatmap_selected_distribution_bar'),

                    ]),
                    dbc.Tab(label="Ministers vs Ministries", children=[

                        dcc.Graph(id='heatmap_minister_vs_ministry'),
                        html.P("Select a Box to view the distribution overtime", style={'text-align': 'center', }),
                        dcc.Graph(id="heatmap_selected_distribution_bar_2")

                    ])
                ], className="nav nav-fill")

            ], className="pretty_container twelve columns"),

        ], className="row flex-display"),

        # NLP
        html.Div([
            # Graph 7: Scatter_3d
            dbc.Row(
                [
                    dbc.Col([html.Div(scatter_col, className="pretty_container h-99")], width=4),
                    dbc.Col([html.Div([dcc.Graph(id='nlp_scatter'),
                                       html.P(
                                           "Click any point to view the complete question, Sizes are re-scaled to show the euclidean distance from clicked point")],
                                      className=" pretty_container")]),

                ], className="", no_gutters=True),

            # card
            html.Div(
                [
                    dbc.Col(dbc.Card(card_content, color="dark", outline=True, ),
                            className="w-50 h-30"),

                    dbc.Col(dbc.Card([
                        dbc.CardHeader(["Most Similar Question to selected Question in all the 89K samples", html.Br(),
                                        "(computed using cosine distance)"]),
                        dbc.CardBody(
                            [
                                html.H5("Card title", className="card-title", id='card_question2'),
                                html.H6("Card ", id='card_question_by2'),
                                html.P(
                                    "This is some card content that we'll reuse",
                                    className="card-text", id='card_text2'
                                ),
                            ]
                        ),
                    ], color="dark", outline=True, ), className="w-50 h-30"),

                ],
                className="row pretty_container w-100"
            ),

        ], className=""),

    ], id="mainContainer", style={
        "display": "flex",
        "flex-direction": "column",
        'justify-content': 'space-around',
    }, )

    @app.callback(
        [Output('total_questions_by_ministry', 'figure'),
         Output('paralle_category_plot_by_party_name', 'figure'), Output('heatmap_state_vs_ministry', 'figure'),
         Output('total_questions_overtime', 'figure'), Output('heatmap_minister_vs_ministry', 'figure')],
        Input('year_slider', 'value'))
    def update_all_figure_to_range(value):
        df_new = append_files(df, str(value[0]), str(value[1]))
        return [total_questions_by_ministry(df_new), paralle_category_plot_by_party_name(df_new),
                heatmap_state_vs_ministry(df_new), questions_overtime_by_ministry(df_new),
                heatmap_miniter_vs_ministry(df_new)]

    @app.callback(
        Output('sunburst', 'figure'),
        Input('total_questions_overtime', 'selectedData'))
    def update_sunburst(selectedData):
        if (selectedData is not None):
            dates = [x['x'] for x in selectedData['points']]
            start, end = dates[0][:7], dates[-1][:7]
            return get_sunburst_figure(df, start, end)
        else:
            return get_sunburst_figure(df, '2011-03', '2011-06')

    @app.callback(
        Output('total_questions_by_ministers', 'figure'),
        Input('total_questions_by_ministry', 'clickData'))
    def update_total_question_by_minsters(clickData):
        if (clickData is not None):
            ministry = clickData['points'][0]['x']
            return ministry_question_by(df, ministry)
        else:
            return ministry_question_by(df, 'HOME AFFAIRS')

    @app.callback(
        Output('number_of_rows', 'value'),
        Input('year_slider', 'value'))
    def update_number_of_rows(value):
        return str((append_files(df, str(value[0]), str(value[1]))).shape[0])

    @app.callback(
        Output('mapbox', 'figure'),
        Input('mapbox-dropdown', 'value'))
    def update_choropleth(value):
        return mapbox_members_questions(value)

    @app.callback(
        Output('mapbox-clicked-data', 'figure'),
        Input('mapbox', 'clickData'), Input('mapbox-dropdown', 'value'))
    def display_click_data(clickData, value):

        if (clickData is not None):
            if value == 'members':
                states = clickData['points'][0]['location']
                return top_members_of_state(states)
            elif value == 'questions':
                states = clickData['points'][0]['location']
                return top_ministry_of_state(states)
        else:
            return top_members_of_state('BIHAR')

    @app.callback(
        Output('nlp_scatter', 'figure'),
        [Input('samplesize', 'value'), Input('perplexity', 'value'), Input('pca-dimension', 'value'),
         Input('scatter_switch', 'value'), Input('nlp_scatter', 'clickData')])
    def update_scatter_plot(samplesize, perplexity, pca, toggle, clickData):
        fig, projection_df = scatter_embedding_with_text(samplesize, pca, perplexity)
        if not toggle:
            fig.update_traces(text="")

        if clickData is not None:
            x, y, z = clickData['points'][0]['x'], clickData['points'][0]['y'], clickData['points'][0]['z']
            point = np.array([x, y, z])
            fig_projections = projection_df.iloc[:, :-1].to_numpy()
            # Compute cosine distances for each projection from clicked point.
            distances = [(index, distance.euclidean(point, value)) for index, value in enumerate(fig_projections)]
            sizes = np.array(distances)[:, 1]
            # Normalize the distance before using as sizes
            sizes = sizes / (sizes.max() / 1)
            scaling_factor = 20
            sizes = (1 - sizes) * scaling_factor
            fig.update_traces(marker_size=sizes)
            fig.update_layout(
                scene=dict(annotations=[
                    dict(x=x, y=y, z=z,
                         text="Selected Question",
                         arrowhead=1,
                         xanchor="left",
                         yanchor="bottom")]), )

            return fig

        return fig

    @app.callback(
        Output('heatmap_selected_distribution_bar', 'figure'),
        [Input('heatmap_state_vs_ministry', 'clickData'), Input('year_slider', 'value')])
    def display_selected_data_heatmap_1(clickData, value):
        if (clickData == None):
            return clicked_data_point_bar_plot('Uttar Pradesh', 'HOME AFFAIRS', str(value[0]),
                                               str(value[1]), append_files(df, str(value[0]), str(value[1])))
        else:
            return clicked_data_point_bar_plot(clickData['points'][0]['x'], clickData['points'][0]['y'], str(value[0]),
                                               str(value[1]), append_files(df, str(value[0]), str(value[1])))

    @app.callback(
        Output('heatmap_selected_distribution_bar_2', 'figure'),
        [Input('heatmap_minister_vs_ministry', 'clickData'), Input('year_slider', 'value')])
    def display_selected_data_heatmap_2(clickData, value):
        if (clickData == None):
            return clicked_datapoint_ministers_vs_mintery('SHRI MOHAN SINGH', 'HOME AFFAIRS', str(value[0]),
                                                          str(value[1]), append_files(df, str(value[0]), str(value[1])))
        else:
            return clicked_datapoint_ministers_vs_mintery(clickData['points'][0]['y'], clickData['points'][0]['x'],
                                                          str(value[0]),
                                                          str(value[1]), append_files(df, str(value[0]), str(value[1])))

    @app.callback(
        [Output('card_question', 'children'), Output('card_question_by', 'children'), Output('card_text', 'children')],
        Input('nlp_scatter', 'clickData'))
    def update_question_card(clickData):
        if (clickData is not None):
            index = clickData['points'][0]['customdata'][0]
            return get_question_from_index(index)
        else:
            return ("No Point Selected", "", "")

    @app.callback(
        [Output('card_question2', 'children'), Output('card_question_by2', 'children'),
         Output('card_text2', 'children')],
        Input('nlp_scatter', 'clickData'))
    def update_similar_question_card(clickData):
        if (clickData is not None):
            index = clickData['points'][0]['customdata'][0]
            return get_similar_question_by_index(index)
        else:
            return ("No Point Selected", "", "")

    return app


if __name__ == '__main__':
    dash_app().run_server(debug=False)
