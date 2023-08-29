
# import calendar
import pandas as pd
# import plotly.express as px
# from plotly.offline import plot


async def pd_data(tracker_data):
    df = pd.DataFrame(tracker_data, columns=['action_name', 'dow', 'track_sum'])
    df = df.pivot(index='dow', columns='action_name', values='track_sum')
    data_lst: list = df.to_records(index=True).tolist()
    headers = df.keys().tolist()
    headers.insert(0, "dow")
    data_lst.insert(0, headers)
    # for i in data_lst[1]:
    #     if isinstance(i, str):
    #         weekday = calendar.day_name[int(i)]
    #         print(weekday)
    #     print(type(i))
    return data_lst

    # create plotly bar
    # fig = px.bar(df, x="dow", y='track_sum', color='action_name', title='Title', barmode='stack')
    # fig.show()


    # Generate your plotly figure as fig
    # div = plot(
    #     fig,
    #     output_type='div',
    #     include_plotlyjs=True
    # )
    # # print(div)
    # with open('my_html.html', mode='w', encoding='utf-8') as f:
    #     f.write(div)
    # return div