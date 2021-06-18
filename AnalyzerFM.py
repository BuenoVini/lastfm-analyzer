from LastFM import LastFM
from HighlighterFM import HighlighterFM
from time import sleep, mktime, localtime, gmtime
from datetime import date
from sys import exit
import requests_cache # type: ignore
import pandas as pd # type: ignore
import numpy as np

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
                sleep(0.25)

            # append current response to pages
            pages.append(response.json())

            # verifying if the current page does not exceed the max page number... if it does (last one), break the loop
            if current_page < int(response.json()['recenttracks']['@attr']['totalPages']):
                current_page += 1
            else:
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

        time_offset = ( mktime(localtime()) - mktime(gmtime()) ) / 3600
        self.df['Date'] = self.df['Date'] + pd.Timedelta(time_offset, 'H')

        self.df.set_index('Date', inplace=True)

        # saving the date of the first and last scrobble
        self.first_day = self.df.index[-1]
        self.last_day = self.df.index[0]

        # empty albums cells means that the song was listened in the Last.fm Web Player
        self.df['Album'] = self.df['Album'].replace('', 'Last.fm Web Player')


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


    def highlights_week(self, week: str) -> HighlighterFM:
        """
        Counts stats like the total and average daily scrobbles, total artists and albums of the current and previous week.

        Paramaters:
            week: Desired week (YYYY-MM-DD).

        Returns:
            A HighlighterFm object with the week's highlights
        """
        last_week = pd.Timestamp(week) - pd.Timedelta(7, 'D')

        return HighlighterFM(
            period='week',

            df_artists_cur=self.top_by_week('Artist', week),
            df_albums_cur=self.top_by_week('Album', week),
            df_tracks_cur=self.top_by_week('Track', week),

            df_artists_last=self.top_by_week('Artist', last_week),
            df_albums_last=self.top_by_week('Album', last_week),
            df_tracks_last=self.top_by_week('Track', last_week)
        )

    
    def highlights_month(self, year_month: str) -> HighlighterFM:
        """
        Counts stats like the total and average daily scrobbles, total artists and albums of the current and previous month.

        Paramaters:
            month: Desired month (YYYY-MM).

        Returns:
            A HighlighterFm object with the month's highlights
        """
        last_month = pd.Timestamp(year_month) - pd.Timedelta(4, 'W')

        return HighlighterFM(
            period='month',

            df_artists_cur=self.top_by_month('Artist', year_month),
            df_albums_cur=self.top_by_month('Album', year_month),
            df_tracks_cur=self.top_by_month('Track', year_month),

            df_artists_last=self.top_by_month('Artist', f"{last_month.year}-{last_month.month}"),
            df_albums_last=self.top_by_month('Album', f"{last_month.year}-{last_month.month}"),
            df_tracks_last=self.top_by_month('Track', f"{last_month.year}-{last_month.month}")
        )

    def highlights_year(self, year: str) -> HighlighterFM:
        """
        Counts stats like the total and average daily scrobbles, total artists and albums of the current and previous year.

        Paramaters:
            year: Desired year (YYYY).

        Returns:
            A HighlighterFm object with the year's highlights
        """
        last_year = str( int(year) - 1 )

        return HighlighterFM(
            period='year',

            df_artists_cur=self.top_by_year('Artist', year),
            df_albums_cur=self.top_by_year('Album', year),
            df_tracks_cur=self.top_by_year('Track', year),

            df_artists_last=self.top_by_year('Artist', last_year),
            df_albums_last=self.top_by_year('Album', last_year),
            df_tracks_last=self.top_by_year('Track', last_year)
        )

    
    def top_by_week(self, category: str, date: str) -> pd.DataFrame:
        """
        Finds the top category (Artist, Track or Album) in the period of one week.
        NOTE: The day passed as parameter is open-ended, meaning that this day is not taken into account.

        Parameters:
            category: Can be either 'Artist', 'Album' or 'Track'.
            date: Desired date (YYYY-MM-DD).

        Returns:
            A list with the top category for the period of one week.
        """
        current_week = pd.Timestamp(date)
        last_week = current_week - pd.Timedelta(7, 'D')

        return self.__top(self.df.loc[current_week:last_week], category)


    def top_by_month(self, category: str, year_month: str) -> pd.DataFrame:
        """
        Finds the top category (Artist, Track or Album) of a specif month of the given year.

        Parameters:
            category: Can be either 'Artist', 'Album' or 'Track'.
            year_month: Desired date (YYYY-MM).

        Returns:
            A list with the top category for the given month.
        """
        return self.__top(self.df.loc[year_month], category)


    def top_by_year(self, category: str, year: str) -> pd.DataFrame:
        """
        Finds the top category (Artist, Track or Album) of the whole year.

        Parameters:
            category: Can be either 'Artist', 'Album' or 'Track'.
            year: Desired year (YYYY).

        Returns:
            A list with the top category for the given year.
        """
        return self.__top(self.df.loc[year], category)



if __name__ == '__main__':
    analyzer = AnalyzerFM('Vini_Bueno')
    # for month in range(1, 6):
    #     print(f"\n2021-{month}", analyzer.top_by_month('Artist', 2021, month)[0:10], sep='\n')

    for year in [2018, 2019, 2020, 2021]:
        print(f"\n{year}", analyzer.top_by_year('Track', str(year)).head(), sep='\n')

    # print("\nLast week:", analyzer.top_by_week('Track', 2021, 6, 3).head(), sep='\n')