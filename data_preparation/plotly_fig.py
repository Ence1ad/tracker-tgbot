import plotly.graph_objs as go
import plotly.offline as pyo

from config import settings
from data_preparation.chart_date_title import DateTitle


async def create_fig(df_action, df_categories, sheet_name=settings.WEEKLY_XLSX_FILE_NAME):
    data = []

    for action_name in df_action['action_name']:
        trace = go.Bar(
            x=df_action['day_of_week'],
            y=df_action[action_name],
            name=action_name
        )
        data.append(trace)

    layout = go.Layout(
        title=f'bars(week - {DateTitle.week})',
        xaxis=dict(title='Days of the Week'),
        yaxis=dict(title='Devoted Time')
    )

    fig = go.Figure(data=data, layout=layout)

    pyo.plot(fig, filename=sheet_name, auto_open=False)

    # Create a pie chart
    pie_data = [go.Pie(
        labels=df_categories['category_name'],
        values=df_categories['duration'],
    )]

    pie_layout = go.Layout(
        title=f'pie(week - {DateTitle.week})'
    )

    pie_fig = go.Figure(data=pie_data, layout=pie_layout)

    pyo.plot(pie_fig, filename=f'pie_{sheet_name}', auto_open=False)