import pandas as pd
from pandas import DataFrame
from sqlalchemy import Row


async def pd_action_data(tracker_data: list[Row]) -> DataFrame:
    df: DataFrame = pd.DataFrame(tracker_data, columns=['action_name', 'category_name', 'dow', 'track_sum'])
    dow_key: list[str] = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    df = df.pivot(index='dow', columns='action_name', values='track_sum').reindex(dow_key)
    return df


async def pd_category_data(tracker_data: list[Row]) -> DataFrame:
    df: DataFrame = pd.DataFrame(tracker_data, columns=['action_name', 'category_name', 'dow', 'track_sum'])
    df: DataFrame = df.groupby(['category_name']).apply(
        lambda dataframe: sum(dataframe["track_sum"])).reset_index(name='duration')
    df.index = df.index + 1
    return df

