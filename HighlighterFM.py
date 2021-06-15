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

        # object.__setattr__(self, 'state', state)

    
    def __str__(self) -> str:
        return f"Current Artists Listened: {self.artists_cur},\nCurrent Albums Listened: {self.albums_cur},\nCurrent Tracks Listened: {self.tracks_cur},\nCurrent Scrobbles: {self.scrobbles_cur},\nCurrent Average Daily: {self.average_daily_cur}\n\nLast Artists Listened: {self.artists_last},\nLast Albums Listened: {self.albums_last},\nLast Tracks Listened: {self.tracks_last},\nLast Scrobbles: {self.scrobbles_last},\nLast Average Daily: {self.average_daily_last}\n"


    @staticmethod
    def __unique(df: pd.DataFrame, category: str) -> int:
        return df.value_counts(category).sum()

    
    @staticmethod
    def __total(df: pd.DataFrame) -> int:
        return df.index.values.sum()