from dataclasses import dataclass
from typing import Tuple
import pandas as pd # type: ignore
# from AnalyzerFM import AnalyzerFM

@dataclass(init=False, frozen=True)
class HighlighterFM:
    period: str

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

    top_artist: pd.Series
    top_album: pd.Series
    top_track: pd.Series


    def __init__(self, period: str, df_artists_cur: pd.DataFrame, df_albums_cur: pd.DataFrame, df_tracks_cur: pd.DataFrame, df_artists_last: pd.DataFrame, df_albums_last: pd.DataFrame, df_tracks_last: pd.DataFrame) -> None:
        if period in 'year month week'.split():
            object.__setattr__(self, 'period', period)
        else:
            raise ValueError(f"period should be: 'year', 'month' or 'week', but '{period}' was passed.")

        object.__setattr__(self, 'artists_cur', self.__unique(df_artists_cur, 'Artist'))
        object.__setattr__(self, 'albums_cur', self.__unique(df_albums_cur, 'Album'))
        object.__setattr__(self, 'tracks_cur', self.__unique(df_tracks_cur, 'Track'))
        object.__setattr__(self, 'scrobbles_cur', self.__total(df_tracks_cur))
        period_map = {'year': 365, 'month': 30, 'week': 7}
        object.__setattr__(self, 'average_daily_cur', round(self.scrobbles_cur / period_map[period]))

        object.__setattr__(self, 'artists_last', self.__unique(df_artists_last, 'Artist'))
        object.__setattr__(self, 'albums_last', self.__unique(df_albums_last, 'Album'))
        object.__setattr__(self, 'tracks_last', self.__unique(df_tracks_last, 'Track'))
        object.__setattr__(self, 'scrobbles_last', self.__total(df_tracks_last))
        object.__setattr__(self, 'average_daily_last', round(self.scrobbles_last / period_map[period]))

        object.__setattr__(self, 'percentage_artists', self.__percentage(self.artists_cur,self.artists_last))        
        object.__setattr__(self, 'percentage_albums', self.__percentage(self.albums_cur,self.albums_last))
        object.__setattr__(self, 'percentage_tracks', self.__percentage(self.tracks_cur,self.tracks_last))
        object.__setattr__(self, 'percentage_scrobbles', self.__percentage(self.scrobbles_cur, self.scrobbles_last))
        object.__setattr__(self, 'percentage_average_daily', self.__percentage(self.average_daily_cur, self.average_daily_last))

        object.__setattr__(self, 'top_artist', df_artists_cur.iloc[0])
        object.__setattr__(self, 'top_album', df_albums_cur.iloc[0])
        object.__setattr__(self, 'top_track', df_tracks_cur.iloc[0])

    
    def __str__(self) -> str:
        return f"""
        --Current {self.period}--
        Total Artists listened: {self.artists_cur}
        Total Albums listened: {self.albums_cur}
        Total Tracks listened: {self.tracks_cur}
        Total Scrobbles: {self.scrobbles_cur}
        Average Daily: {self.average_daily_cur}
        
        --Previous {self.period}--
        Total Artists listened: {self.artists_last}
        Total Albums listened: {self.albums_last}
        Total Tracks listened: {self.tracks_last}
        Total Scrobbles: {self.scrobbles_last}
        Average Daily: {self.average_daily_last}
        
        --Statistics vs. previous {self.period}--
        Total Artists listened: {self.percentage_artists}%
        Total Albums listened: {self.percentage_albums}%
        Total Tracks listened: {self.percentage_tracks}%
        Total Scrobbles: {self.percentage_scrobbles}%
        Average Daily: {self.percentage_average_daily}%

        --Top listened--
        Artist: {self.top_artist['Artist']} with {self.top_artist.name} scrobbles
        Album: {self.top_album['Album']} by {self.top_album['Artist']} with {self.top_album.name} scrobbles
        Track: {self.top_track['Track']} from {self.top_track['Album']} by {self.top_track['Artist']} with {self.top_track.name} scrobbles
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
