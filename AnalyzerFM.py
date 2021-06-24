from LastFM import LastFM
from HighlighterFM import HighlighterFM
from time import sleep, mktime, localtime, gmtime
from datetime import date
from sys import exit
import requests_cache # type: ignore
import pandas as pd # type: ignore
import numpy as np
from IPython.core.display import clear_output # type: ignore

class AnalyzerFM():
    """
    An analyzer for the user's data fetched from Last.fm.

    Public instance variables:
        df: Dataframe with all scrobbles information of that user.
        first_day: The day of the first scrobble of that user.
        last_day: The day of the last scrobble of that user.

    Public methods:
        TODO
    """
    def __init__(self, user: str) -> None:
        """
        Constructs the user's dataframe used for the Analyzer.

        Parameters:
            user: Last.fm username

        Returns:
            None.
        """
        api = LastFM()
        pages = []
        current_page = 1

        requests_cache.install_cache('cached_request')      # caching the get request in cached_request.sqlite for faster performance

        # looping through all the response pages 
        while True:
            response = api.get_recent_tracks(user, '2018-01-01', date.today().strftime("%Y-%m-%d"), limit=200, page=current_page) # getting the user's recent tracks, page by page
            
            # verifying if the response was OK... if not print message and exit with error
            if response.status_code != 200:
                print(response.text)
                exit(1)
            
            # verifying if the response came from the server (and not from the cache)
            if not getattr(response, 'from_cache', False):
                print(response.status_code, current_page, response.json()['recenttracks']['@attr']['totalPages'])
                clear_output(wait=True)
                sleep(0.25)

            # append current response to pages
            pages.append(response.json())

            # verifying if the current page does not exceed the max page number... if it does (last one), break the loop
            if current_page < int(response.json()['recenttracks']['@attr']['totalPages']):
                current_page += 1
            else:
                print("All pages fetched!")
                break
        
        # creating the dataframe to be used by the Analyzer
        self.df = pd.DataFrame({
            'Artist': [ scrobble['artist']['#text'] for page in pages for scrobble in page['recenttracks']['track'] ],
            'Album': [ scrobble['album']['#text'] for page in pages for scrobble in page['recenttracks']['track'] ],
            'Track': [ scrobble['name'] for page in pages for scrobble in page['recenttracks']['track'] ],
            'Date': [ scrobble['date']['#text'] for page in pages for scrobble in page['recenttracks']['track'] ]
        })

        # converting the Date column from string to datetime64, converting it to local timezone times and setting it as index
        self.df['Date'] = pd.to_datetime(self.df['Date'], format='%d %b %Y, %H:%M')

        time_offset = ( mktime(localtime()) - mktime(gmtime()) ) / 3600 # TODO: use api._timezone_offset
        self.df['Date'] = self.df['Date'] + pd.Timedelta(time_offset, 'H')

        self.df.set_index('Date', inplace=True)

        # saving the date of the first and last scrobble
        self.first_day = self.df.index[-1]
        self.last_day = self.df.index[0]

        # empty albums cells means that the song was listened in the Last.fm Web Player
        self.df['Album'] = self.df['Album'].replace('', 'Last.fm Web Player')


    @staticmethod
    def __validate_period(period: str) -> None:
        """Verifies if the period string is valid, if not a ValueError is raised."""
        if period not in 'year month week'.split():
            raise ValueError(f"period should be: 'year', 'month' or 'week', but '{period}' was passed.")

    
    @staticmethod
    def __percentage(current_total: int, previous_total: int) -> int:
        """Calculates the percentage between the current vs last period of the given field."""
        # checking if at least one total is different than zero
        if (current_total or previous_total) != 0:
            previous_total = max(1, previous_total)     # avoiding division by zero
            return round( ((current_total / previous_total) - 1) * 100 )
        else:
            return 0    # no scrobbles during the current and last period: 0%


    @staticmethod
    def __top(df: pd.DataFrame, category: str) -> pd.DataFrame:
        """Finds the top category (how many times an Artist, Track or Album was scrobbled) in the given dataframe and returns a new dataframe with them."""
        new_df = df.copy()

        if category == 'Track':
            new_df['Count'] = new_df.groupby(['Track', 'Artist']).transform('count')
            new_df.drop_duplicates(['Track', 'Artist'], inplace=True)

            # sorting by count, then artist and then by track
            return new_df.iloc[ np.lexsort([new_df['Track'].str.upper(), new_df['Artist'].str.upper(), -new_df['Count']]) ].reset_index(drop=True)
        
        elif category == 'Album':
            new_df = new_df[ ~(new_df['Album'] == 'Last.fm Web Player') ]     # dropping the songs that were listened in Last.fm Web Player
            
            new_df['Count'] = new_df.groupby(['Album', 'Artist']).transform('count')
            new_df = new_df.drop_duplicates(['Album', 'Artist']).drop('Track', axis='columns')

            # sorting by count, then artist and then by album
            return new_df.iloc[ np.lexsort([new_df['Album'].str.upper(), new_df['Artist'].str.upper(), -new_df['Count']]) ].reset_index(drop=True)

        elif category == 'Artist':
            new_df['Count'] = new_df.groupby('Artist').transform('count')['Album']
            new_df = new_df.drop_duplicates('Artist').drop(['Track', 'Album'], axis='columns')

            # sorting by count and then by artist
            return new_df.iloc[ np.lexsort([new_df['Artist'].str.upper(), -new_df['Count']]) ].reset_index(drop=True)
        
        else:
            raise ValueError(f"category should be: 'Artist', 'Album' or 'Track', but '{category}' was passed.")


    def top_by(self, period: str, category: str, date: str) -> pd.DataFrame:    # TODO: change to top_by(self, period: str, date: str, category: str)
        # verifying if the period passed is valid
        self.__validate_period(period)

        if period == 'year' or period == 'month':
            return self.__top(self.df.loc[date], category)

        else: # period == 'week':
            current_week = pd.Timestamp(date)
            last_week = current_week - pd.Timedelta(7, 'D')
            current_week -= pd.Timedelta(1, 'S')    # TODO: should I change the approach to this problem ??

            return self.__top(self.df.loc[current_week:last_week], category)


    def highlights_of(self, period: str, date: str) -> HighlighterFM:
        # verifying if the period passed is valid
        self.__validate_period(period)

        # creating the dataframes with artists, albums, and tracks of the given period
        df_artists = self.top_by(period, 'Artist', date)
        df_albums = self.top_by(period, 'Album', date)
        df_tracks = self.top_by(period, 'Track', date)

        # computing the fields of the given period
        total_artists = df_artists.value_counts('Artist').sum()
        total_albums = df_albums.value_counts('Album').sum()
        total_tracks = df_tracks.value_counts('Track').sum()
        total_scrobbles = df_tracks['Count'].sum()
        average_daily = round(total_scrobbles / {'year': 365, 'month': 30, 'week': 7}[period])

        # finding the most listened artist, album, and track name
        if not df_tracks.empty:
            df_top_artist = df_artists.iloc[0]
            df_top_album = df_albums.iloc[0]
            df_top_track = df_tracks.iloc[0]
        else:
            df_top_artist = pd.Series(data={'Artist': '-', 'Count': 0})
            df_top_album = pd.Series(data={'Artist': '-', 'Album': '-', 'Count': 0})
            df_top_track = pd.Series(data={'Artist': '-', 'Album': '-', 'Track': '-', 'Count': 0})
        
        # setting the HighlighterFM fields and returning it
        return HighlighterFM(
            period,
            total_artists,
            total_albums,
            total_tracks,
            total_scrobbles,
            average_daily,
            df_top_artist,
            df_top_album,
            df_top_track
        )


    def summary_highlights(self, period: str, date: str) -> str:
        # verifying if the period passed is valid
        self.__validate_period(period)

        # computing the highlights of the current date
        current_highlights = self.highlights_of(period, date)

        # computing the highlights of the previous date
        if period == 'year':
            previous_date = pd.Timestamp.strftime(pd.Timestamp(date) - pd.Timedelta(52, 'W'), format='%Y')

        elif period == 'month':
            previous_date = pd.Timestamp.strftime(pd.Timestamp(date) - pd.Timedelta(4, 'W'), format='%Y-%m')

        else: # period == 'week':
            previous_date = pd.Timestamp.strftime(pd.Timestamp(date) - pd.Timedelta(1, 'W'), format='%Y-%m-%d')
        
        previous_highlights = self.highlights_of(period, previous_date)

        # computing the percentage
        percentage_artists = self.__percentage(current_highlights.total_artists, previous_highlights.total_artists)
        percentage_albums = self.__percentage(current_highlights.total_albums, previous_highlights.total_albums)
        percentage_tracks = self.__percentage(current_highlights.total_tracks, previous_highlights.total_tracks)
        percentage_scrobbles = self.__percentage(current_highlights.total_scrobbles, previous_highlights.total_scrobbles)
        percentage_average_daily = self.__percentage(current_highlights.average_daily, previous_highlights.average_daily)

        # returning the message with the highlights compared with the previous date
        return f"""
        --{period.title()}: {date}--
        Total Artists listened: {current_highlights.total_artists}
        Total Albums listened: {current_highlights.total_albums}
        Total Tracks listened: {current_highlights.total_tracks}
        Total Scrobbles: {current_highlights.total_scrobbles}
        Average Daily: {current_highlights.average_daily}
        
        --Previous {period}: {previous_date}--
        Total Artists listened: {previous_highlights.total_artists}
        Total Albums listened: {previous_highlights.total_albums}
        Total Tracks listened: {previous_highlights.total_tracks}
        Total Scrobbles: {previous_highlights.total_scrobbles}
        Average Daily: {previous_highlights.average_daily}
        
        --Statistics vs. previous {period}--
        Total Artists listened: {percentage_artists}%
        Total Albums listened: {percentage_albums}%
        Total Tracks listened: {percentage_tracks}%
        Total Scrobbles: {percentage_scrobbles}%
        Average Daily: {percentage_average_daily}%

        --Top listened--
        Artist: {current_highlights.df_top_artist['Artist']} with {current_highlights.df_top_artist['Count']} scrobbles
        Album: {current_highlights.df_top_album['Album']} by {current_highlights.df_top_album['Artist']} with {current_highlights.df_top_album['Count']} scrobbles
        Track: {current_highlights.df_top_track['Track']} from {current_highlights.df_top_track['Album']} by {current_highlights.df_top_track['Artist']} with {current_highlights.df_top_track['Count']} scrobbles
        """
