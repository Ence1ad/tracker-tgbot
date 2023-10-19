import pandas as pd
from pandas import DataFrame
from sqlalchemy import Sequence


async def pd_action_data(tracker_data: Sequence) -> DataFrame:
    """Prepare a Pandas DataFrame for action data from the tracker_data.

    :param tracker_data: Sequence: A sequence containing tracker data.
    :return: DataFrame: A Pandas DataFrame with action data.
    """
    df: DataFrame = pd.DataFrame(tracker_data,
                                 columns=['action_name', 'category_name', 'dow',
                                          'track_sum'])
    dow_key: list[str] = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
    df = df.pivot(index='dow', columns='action_name', values='track_sum').reindex(
        dow_key)
    return df


async def pd_category_data(tracker_data: Sequence) -> DataFrame:
    """Prepare a Pandas DataFrame for category data from the tracker_data.

    :param tracker_data: Sequence: A sequence containing tracker data.
    :return: DataFrame: A Pandas DataFrame with category data.
    """
    df: DataFrame = pd.DataFrame(tracker_data,
                                 columns=['action_name', 'category_name', 'dow',
                                          'track_sum'])
    df: DataFrame = df.groupby(['category_name']).apply(
        lambda dataframe: sum(dataframe["track_sum"])).reset_index(name='duration')
    df.index = df.index + 1
    return df
