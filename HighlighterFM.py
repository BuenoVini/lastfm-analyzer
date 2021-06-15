from dataclasses import dataclass
import pandas as pd # type: ignore
# from AnalyzerFM import AnalyzerFM

@dataclass(init=False, frozen=True)
class HighlighterFM:
    artists_cur: int
    albums_cur: int
    tracks_cur: int
    scrobbles_cur: int
    average_daily_cur: int

    artists_last: int
    albums_last: int
    tracks_last: int
    scrobbles_last: int
    average_daily_last: int

    percentage_artists: int
    percentage_albums: int
    percentage_tracks: int
    percentage_scrobbles: int
    percentage_average_daily: int

    # state: str


    def __init__(self, df_artists_cur: pd.DataFrame, df_albums_cur: pd.DataFrame, df_tracks_cur: pd.DataFrame, df_artists_last: pd.DataFrame, df_albums_last: pd.DataFrame, df_tracks_last: pd.DataFrame) -> None:
        object.__setattr__(self, 'artists_cur', self.__unique(df_artists_cur, 'Artist'))
        object.__setattr__(self, 'albums_cur', self.__unique(df_albums_cur, 'Album'))
        object.__setattr__(self, 'tracks_cur', self.__unique(df_tracks_cur, 'Track'))
        object.__setattr__(self, 'scrobbles_cur', self.__total(df_tracks_cur))
        object.__setattr__(self, 'average_daily_cur', round(self.scrobbles_cur / 7))

        object.__setattr__(self, 'artists_last', self.__unique(df_artists_last, 'Artist'))
        object.__setattr__(self, 'albums_last', self.__unique(df_albums_last, 'Album'))
        object.__setattr__(self, 'tracks_last', self.__unique(df_tracks_last, 'Track'))
        object.__setattr__(self, 'scrobbles_last', self.__total(df_tracks_last))
        object.__setattr__(self, 'average_daily_last', round(self.scrobbles_last / 7))

        object.__setattr__(self, 'percentage_artists', self.__percentage(self.artists_cur,self.artists_last))        
        object.__setattr__(self, 'percentage_albums', self.__percentage(self.albums_cur,self.albums_last))
        object.__setattr__(self, 'percentage_tracks', self.__percentage(self.tracks_cur,self.tracks_last))
        object.__setattr__(self, 'percentage_scrobbles', self.__percentage(self.scrobbles_cur, self.scrobbles_last))
        object.__setattr__(self, 'percentage_average_daily', self.__percentage(self.average_daily_cur, self.average_daily_last))

        # object.__setattr__(self, 'state', state)

    
    def __str__(self) -> str:
        return f"""
        Current Artists listened: {self.artists_cur},
        Current Albums listened: {self.albums_cur},
        Current Tracks listened: {self.tracks_cur},
        Current Scrobbles: {self.scrobbles_cur},
        Current Average Daily: {self.average_daily_cur}
        
        Last time Artists listened: {self.artists_last},
        Last time Albums listened: {self.albums_last},
        Last time Tracks listened: {self.tracks_last},
        Last time Scrobbles: {self.scrobbles_last},
        Last time Average Daily: {self.average_daily_last}
        
        Total Artists compared to last time: {self.percentage_artists}%,
        Total Albums compared to last time: {self.percentage_albums}%,
        Total Tracks compared to last time: {self.percentage_tracks}%,
        Total Scrobbles compared to last time: {self.percentage_scrobbles}%,
        Average Daily compared to last time: {self.percentage_average_daily}%,
        """


    @staticmethod
    def __unique(df: pd.DataFrame, category: str) -> int:
        return df.value_counts(category).sum()

    
    @staticmethod
    def __total(df: pd.DataFrame) -> int:
        return df.index.values.sum()


    @staticmethod
    def __percentage(current: int, last: int) -> int:
        return round( ((current / last) - 1) * 100 )