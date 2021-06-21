from dataclasses import dataclass
from typing import Tuple
import pandas as pd # type: ignore
# from AnalyzerFM import AnalyzerFM

@dataclass(init=False, frozen=True)
class HighlighterFM:
    """
    A data class with a bunch of statistics based on Artists, Albums and Tracks. The analysis is done comparing a current date and the previous date.

    Public fields:
        period: Indicates whether it is a year, month or week highlight.

        total_artists: Total Artists scrobbled in the current period.
        total_albums: Total Albums scrobbled in the current period.
        total_tracks: Total Tracks scrobbled in the current period.
        total_scrobbles: Total scrobbles in the current period.
        average_daily: Average daily of scrobbles in the current period.

        total_artists_last: Total Artists scrobbled in the last period.
        total_albums_last: Total Albums scrobbled in the last period.
        total_tracks_last: Total Tracks scrobbled in the last period.
        total_scrobbles_last: Total scrobbles in the last period.
        average_daily_last: Average daily of scrobbles in the last period.

        percentage_artists: Percentage between the total Artists in the current vs. last period.
        percentage_albums: Percentage between the total Albums in the current vs. last period.
        percentage_tracks: Percentage between the total Tracks in the current vs. last period.
        percentage_scrobbles: Percentage between the total scrobbles in the current vs. last period.
        percentage_average_daily: Percentage between the average daily scrobbles in the current vs. last period.

        df_top_artist: The name of the most listened Artist in the current period.
        df_top_album: The name of the most listened Album and Artist in the current period.
        df_top_track: The name of the most listened Track, Album and Artist in the current period.

    Public methods:
        None.
    """
    period: str

    total_artists: int
    total_albums: int
    total_tracks: int
    total_scrobbles: int
    average_daily: int

    total_artists_last: int     # TODO: should they be private ??
    total_albums_last: int
    total_tracks_last: int
    total_scrobbles_last: int
    average_daily_last: int

    percentage_artists: int
    percentage_albums: int
    percentage_tracks: int
    percentage_scrobbles: int
    percentage_average_daily: int

    df_top_artist: pd.Series
    df_top_album: pd.Series
    df_top_track: pd.Series


    def __init__(self, period: str, df_artists_cur: pd.DataFrame, df_albums_cur: pd.DataFrame, df_tracks_cur: pd.DataFrame, df_artists_last: pd.DataFrame, df_albums_last: pd.DataFrame, df_tracks_last: pd.DataFrame) -> None:
        """
        Initializes the class' fields calculating all of their values.

        Parameters:
            period: The period selected (either 'year', 'month' or 'week')
            df_artists_cur: Dataframe with the top Artists in the current period.
            df_albums_cur: Dataframe with the top Albums in the current period.
            df_tracks_cur: Dataframe with the top Tracks in the current period.
            df_artists_last: Dataframe with the top Artists in the last period.
            df_albums_last: Dataframe with the top Albums in the last period.
            df_tracks_last: Dataframe with the top Tracks in the last period.

        Returns:
            None.
        """
        # verifying if the period passed is valid, if not a ValueError is raised
        if period in 'year month week'.split():
            object.__setattr__(self, 'period', period)
        else:
            raise ValueError(f"period should be: 'year', 'month' or 'week', but '{period}' was passed.")

        period_map = {'year': 365, 'month': 30, 'week': 7}
        # since dataclass is frozen (to prevent the user from changing the fields' values) the assignment must be done through __setattr__()
        # initializing the fields of the current period
        object.__setattr__(self, 'total_artists', self.__unique(df_artists_cur, 'Artist'))
        object.__setattr__(self, 'total_albums', self.__unique(df_albums_cur, 'Album'))
        object.__setattr__(self, 'total_tracks', self.__unique(df_tracks_cur, 'Track'))
        object.__setattr__(self, 'total_scrobbles', self.__total(df_tracks_cur))
        object.__setattr__(self, 'average_daily', round(self.total_scrobbles / period_map[period]))

        # initializing the fields of the last period
        object.__setattr__(self, 'total_artists_last', self.__unique(df_artists_last, 'Artist'))
        object.__setattr__(self, 'total_albums_last', self.__unique(df_albums_last, 'Album'))
        object.__setattr__(self, 'total_tracks_last', self.__unique(df_tracks_last, 'Track'))
        object.__setattr__(self, 'total_scrobbles_last', self.__total(df_tracks_last))
        object.__setattr__(self, 'average_daily_last', round(self.total_scrobbles_last / period_map[period]))

        # initializing the percentage fields
        object.__setattr__(self, 'percentage_artists', self.__percentage(self.total_artists, self.total_artists_last))
        object.__setattr__(self, 'percentage_albums', self.__percentage(self.total_albums, self.total_albums_last))
        object.__setattr__(self, 'percentage_tracks', self.__percentage(self.total_tracks, self.total_tracks_last))
        object.__setattr__(self, 'percentage_scrobbles', self.__percentage(self.total_scrobbles, self.total_scrobbles_last))
        object.__setattr__(self, 'percentage_average_daily', self.__percentage(self.average_daily, self.average_daily_last))

        # initializing the most listened artist, album and track name
        if not df_tracks_cur.empty:
            object.__setattr__(self, 'df_top_artist', df_artists_cur.iloc[0])
            object.__setattr__(self, 'df_top_album', df_albums_cur.iloc[0])
            object.__setattr__(self, 'df_top_track', df_tracks_cur.iloc[0])
        else:
            object.__setattr__(self, 'df_top_artist', pd.Series(data={'Artist': '-', 'Count': 0}))
            object.__setattr__(self, 'df_top_album', pd.Series(data={'Artist': '-', 'Album': '-', 'Count': 0}))
            object.__setattr__(self, 'df_top_track', pd.Series(data={'Artist': '-', 'Album': '-', 'Track': '-', 'Count': 0}))

    
    def __str__(self) -> str:   # TODO: show date in print
        return f"""
        --Current {self.period}--
        Total Artists listened: {self.total_artists}
        Total Albums listened: {self.total_albums}
        Total Tracks listened: {self.total_tracks}
        Total Scrobbles: {self.total_scrobbles}
        Average Daily: {self.average_daily}
        
        --Previous {self.period}--
        Total Artists listened: {self.total_artists_last}
        Total Albums listened: {self.total_albums_last}
        Total Tracks listened: {self.total_tracks_last}
        Total Scrobbles: {self.total_scrobbles_last}
        Average Daily: {self.average_daily_last}
        
        --Statistics vs. previous {self.period}--
        Total Artists listened: {self.percentage_artists}%
        Total Albums listened: {self.percentage_albums}%
        Total Tracks listened: {self.percentage_tracks}%
        Total Scrobbles: {self.percentage_scrobbles}%
        Average Daily: {self.percentage_average_daily}%

        --Top listened--
        Artist: {self.df_top_artist['Artist']} with {self.df_top_artist['Count']} scrobbles
        Album: {self.df_top_album['Album']} by {self.df_top_album['Artist']} with {self.df_top_album['Count']} scrobbles
        Track: {self.df_top_track['Track']} from {self.df_top_track['Album']} by {self.df_top_track['Artist']} with {self.df_top_track['Count']} scrobbles
        """


    @staticmethod
    def __unique(df: pd.DataFrame, category: str) -> int:
        """Calculates the unique values from the category. That is, it counts how many unique Artist/Album/Track there is in the dataframe."""
        return df.value_counts(category).sum()

    
    @staticmethod
    def __total(df: pd.DataFrame) -> int:
        """Calculates the total amount of scrobbles of the category. That is, it counts how many Artist/Album/Track was scrobbled in the dataframe."""
        return df['Count'].sum()


    @staticmethod
    def __percentage(total_cur: int, total_last: int) -> int:
        """Calculates the percentage between the current vs last period of the given field."""
        # checking if at least one total is different than zero
        if (total_cur or total_last) != 0:
            total_last = max(1, total_last)     # avoiding division by zero
            return round( ((total_cur / total_last) - 1) * 100 )
        else:
            return 0    # no scrobbles during the current and last period: 0%
