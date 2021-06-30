from dataclasses import dataclass
import pandas as pd # type: ignore

@dataclass(frozen=True)
class HighlighterFM:
    """
    A data class with highlights of a specific period of Artists, Albums and Tracks.

    Public fields:
        period: Indicates whether it is a year, month or week highlight.

        total_artists: Total Artists scrobbled in the current period.
        total_albums: Total Albums scrobbled in the current period.
        total_tracks: Total Tracks scrobbled in the current period.
        total_scrobbles: Total scrobbles in the current period.
        average_daily: Average daily of scrobbles in the current period.

        df_top_artist: The name of the most listened Artist in the current period and its count.
        df_top_album: The name of the most listened Album and Artist in the current period and its count.
        df_top_track: The name of the most listened Track, Album and Artist in the current period and its count.

    Public methods:
        None.
    """
    period: str

    total_artists: int
    total_albums: int
    total_tracks: int
    total_scrobbles: int
    average_daily: int

    df_top_artist: pd.Series
    df_top_album: pd.Series
    df_top_track: pd.Series
