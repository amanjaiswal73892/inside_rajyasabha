import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
import json

from preprocessing import append_files, sortby_datetime, getDataFrameWithPartyName

token = open(".mapbox_token").read()


def mapbox_members_questions(value):
    """ This function is to used to plot the chloropeth graph using a different dataset"""
    states = pd.read_csv('Dataset/statescsv.csv')
    with open('assets/India.json') as f:
        India_states = json.load(f)

    df = pd.read_csv('Dataset/members_from_states.csv')
    if value == 'members':
        fig = px.choropleth(df, geojson=India_states, locations='st_nm',
                            color='count',
                            color_continuous_scale="Viridis",
                            range_color=(0, 44),
                            featureidkey="properties.state_name",
                            projection="mercator",title='Demographic distribution of Rajya Sabha Members'
                            )
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})

    if value == 'questions':
        fig = px.choropleth(df, geojson=India_states, locations='st_nm',
                            color='question_count',
                            color_continuous_scale="Viridis",
                            range_color=(0, 3038),
                            featureidkey="properties.state_name",
                            projection="mercator", title='Demographic distribution of Rajya Sabha Members'
                            )
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0} , )

    return fig


def top_ministry_of_state(stateName):
    """This function is to used to plot a pie chart with the most popular ministries in a state."""
    df = getDataFrameWithPartyName(pd.read_csv('Dataset/Complete_sorted_by_date.csv'))
    df.loc[:, 'State Name'] = df['State Name'].apply(lambda x: str(x).upper())
    df = df.loc[df['State Name'] == stateName]
    group = df['ministry'].value_counts().head(5)
    fig = px.pie(values=group, names=group.index, color=group.index,
                 title="Top ministries questioned by members from " + str(stateName))
    fig.update_layout()
    return fig


def top_members_of_state(stateName):
    """ This function is to used to plot pie chart with most active ministries in a state."""
    df = getDataFrameWithPartyName(pd.read_csv('Dataset/Complete_sorted_by_date.csv'))
    df.loc[:, 'State Name'] = df['State Name'].apply(lambda x: str(x).upper())
    df = df.loc[df['State Name'] == stateName]
    group = df['question_by'].value_counts().head(5)
    fig = px.pie(values=group, names=group.index, color=group.index,
                 title="Most active ministers from " + str(stateName))
    fig.update_layout()

    return fig



def total_questions_by_ministry(df):
    """ This function is to used to plot bar chart with ministries on x-axis. The ministeries are sorted with thier Popularity."""  
    df = df.copy(deep=True)
    group = df.groupby('ministry').apply(len)
    group = group.sort_values(ascending=False)
    fig = px.bar(group, color=group.index, text=group.tolist())
    fig.layout.title = "Total Questions Vs Ministries"
    fig.layout.showlegend = True
    fig.update_xaxes(showticklabels=False)
    fig.update_layout(legend_title="Ministries Sorted by number of question asked",
                      legend_bordercolor='grey', legend_borderwidth=1, legend_font_size=8)
    fig.update_yaxes(title="Total Number Of Questions Asked")
    fig.update_xaxes(title="Various Ministries")

    return fig


def ministry_question_by(df, ministry):
    """ This function is to used to plot bar chart with ministers on x-axis. The ministers are sorted with thier value_counts"""  
    df = df.copy(deep=True)
    group_ministry = df.groupby('ministry')
    group = group_ministry.get_group(ministry).groupby('question_by').apply(len)
    group = group.sort_values(ascending=False)
    fig = px.bar(group, color=group.index)
    fig.layout.title = str(ministry) + " :Total Questions Vs Ministers"
    fig.layout.showlegend = True
    fig.update_xaxes(showticklabels=False)
    fig.update_layout(legend_title="Ministers Sorted by number of question asked",
                      legend_bordercolor='grey', legend_borderwidth=1, legend_font_size=8)
    fig.update_yaxes(title="Total Number Of Questions")
    fig.update_xaxes(title="Various Ministers")

    return fig


def questions_overtime_by_ministry(df):
    """ This function is to used to plot bar chart with ministers on x-axis. The ministers are sorted with thier value_counts"""  
    df = df.copy(deep=True)
    df = df.reset_index(drop=True)
    group = df.groupby(['answer_date', 'ministry'], as_index=False).agg(len)
    fig = px.histogram(group, x='answer_date', y='answer', color='ministry', marginal='box')
    fig.layout.title = "Question Distribution Overtime"
    fig.update_xaxes(
        dtick="M1",
        tickformat="%Y",
        ticklabelmode="period")
    fig.update_layout(legend_title="Ministeries",
                      legend_bordercolor='grey', legend_borderwidth=1, legend_font_size=8)
    fig.update_traces(visible='legendonly')
    fig.update_layout(legend={'itemsizing': 'constant'})
    fig.update_layout(margin_l=10)
    fig.update_layout(margin_r=10)
    return fig


def paralle_category_plot_by_party_name(df):
    """This function is used to plot the parallel category chart by including party affiliations and State from a different dataset."""
    data = df.copy(deep=True)
    dataFrame = getDataFrameWithPartyName(data)
    dataFrame = dataFrame[dataFrame['Party Name'].notna()]
    fig = px.parallel_categories(dataFrame, color=dataFrame['State Name'].apply(lambda x: len(str(x))),
                                 dimensions=[dataFrame['State Name'], dataFrame['Party Name'],
                                             dataFrame.ministry],
                                 labels={'State Name': 'State Name', 'Party Name': "Party Name",
                                         'ministry': 'Ministry', 'question_type': 'Question Type'}, title='Tracing questions to states, ministries, and party name')
    fig.update_layout(coloraxis_showscale=False)
    fig.update_layout(
        margin=dict(l=200, r=250, t=50, b=50),
        autosize=True ,
        height= 800 )
    fig.update_traces(labelfont_size=18)
    fig.update_layout(margin_l=40)
    return fig


def get_sunburst_figure(df, start, end):
    """ This function is used for creating a sunburst chart within the given time range"""
    df = df.copy(deep=True)
    df.index = pd.to_datetime(df.answer_date)
    df = df.loc[start:end, :]
    fig = px.sunburst(df, path=[df.index.year, df.index.month_name(), 'ministry'], color='ministry')
    fig.layout.title = "Sunburst Chart for the period " + start + " : " + end
    fig.update_layout(title_font_size=14)
    fig.update_layout(margin_l=40)
    fig.update_layout(margin_r=40)
    fig.update_layout(margin_t=0)
    fig.update_layout(margin_b=40)
    fig.update_layout(title_y=0.98)
    return fig



def heatmap_state_vs_ministry(df):
    """This function is used to create a density heatmap with State on x-axis and minstries on y-axis. The labels are sorted by thier value_counts."""
    data = df.copy(deep=True)
    dataFrame = getDataFrameWithPartyName(data)
    # We sort the axis on the basis of their value_counts
    order = { 'State Name' :pd.value_counts(dataFrame['State Name'],ascending=False).index.values,
            'ministry' :pd.value_counts(dataFrame['ministry'],ascending=True).index.values}
    fig = px.density_heatmap(dataFrame, x="State Name", y="ministry", 
                             title="Questions asked from different States related to different Ministries",
                             category_orders = order)
    fig.update_layout(
        autosize=False,
        height=900,
    )
    fig.update_yaxes(tickfont_size=5)
    return fig




def heatmap_miniter_vs_ministry(df):
    """This function is used to create a density heatmap with ministry on x-axis and ministers on y-axis. The labels are sorted by thier value_counts."""
    data = df.copy(deep=True)
    dataFrame = getDataFrameWithPartyName(data)
    # We sort the axis on the basis of their value_counts
    order = { 'question_by' :pd.value_counts(dataFrame['question_by'],ascending=True).index.values,
            'ministry' :pd.value_counts(dataFrame['ministry'],ascending=False).index.values}
    fig = px.density_heatmap(dataFrame, x="ministry", y="question_by", 
                             title="Ministers vs Ministries",
                             category_orders = order
                              )
    fig.update_layout(
        autosize=False,
        height=900,
    )
    fig.update_yaxes(tickfont_size=5)
    fig.update_xaxes(tickfont_size=8)
    fig.update_xaxes(tickangle=45)
    return fig


def clicked_data_point_bar_plot(stateName, ministry, minYear, maxYear, df):
    """ This function creates a bar-chart from the clicked points in the heatmap."""
    dataCopy = df.copy(deep=True)
    dataFrame = getDataFrameWithPartyName(dataCopy)
    dataFrame.index = pd.to_datetime(dataFrame.answer_date)
    dataFrame = dataFrame.loc[minYear:maxYear, :]
    dataFrame.drop(['answer_date'], axis=1, inplace=True)
    dataFrame = dataFrame.reset_index()
    dataFrame['year'] = pd.DatetimeIndex(dataFrame['answer_date']).year

    data = dataFrame.groupby(['State Name', 'year', 'ministry'], as_index=False).agg(len)
    data = data[data['ministry'] == ministry]
    titleForBar = 'Questions from ' + stateName + " state related to " + ministry
    data = data[data['State Name'] == stateName]
    fig = px.bar(data, x='year', y='question_by', labels={'question_by': 'Question Count'}, title=titleForBar,
                 color=data.year)
    fig.update_xaxes(
        dtick="M1",
        tickformat="Y",
        ticklabelmode="period")
    fig.update_layout(coloraxis_showscale=False)
    fig.add_trace(go.Line(x=data['year'], y=data['question_by']))

    return fig

def clicked_datapoint_ministers_vs_mintery(minister, ministry, minYear, maxYear, df):
    """ This function creates a bar-chart from the clicked points in the heatmap."""
    dataCopy = df.copy(deep=True)
    dataFrame = getDataFrameWithPartyName(dataCopy)
    dataFrame.index = pd.to_datetime(dataFrame.answer_date)
    dataFrame = dataFrame.loc[minYear:maxYear, :]
    dataFrame.drop(['answer_date'], axis=1, inplace=True)
    dataFrame = dataFrame.reset_index()
    dataFrame['year'] = pd.DatetimeIndex(dataFrame['answer_date']).year

    data = dataFrame.groupby(['question_by', 'year', 'ministry'], as_index=False).agg(len)
    data = data[data['ministry'] == ministry]
    titleForBar = 'Questions from ' + minister + " related to " + ministry
    data = data[data['question_by'] == minister]
    fig = px.bar(data, x='year', y='answer', labels={'answer': 'Question Count'}, title=titleForBar,
                 color=data.year)
    fig.update_xaxes(
        dtick="M1",
        tickformat="Y",
        ticklabelmode="period")
    fig.update_layout(coloraxis_showscale=False)
    fig.add_trace(go.Line(x= data.year,y=data.answer))

    return fig



if __name__ == '__main__':
    top_ministry_of_state('BIHAR')
