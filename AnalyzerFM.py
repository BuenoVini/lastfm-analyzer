from typing import Dict
from time import sleep
from LastFM import LastFM
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

    Public methods:
        None.
    """
    def __init__(self, user: str) -> None:
        """Constructs the user's dataframe used for the Analyzer."""
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

        # converting the Date column from string to datetime64 and setting it as index
        self.df['Date'] = pd.to_datetime(self.df['Date'], format='%d %b %Y, %H:%M')
        self.df.set_index('Date', inplace=True)

        # empty albums cells means that the song was listened in the Last.fm Web Player
        self.df['Album'] = self.df['Album'].replace('', 'Last.fm Web Player')


    @staticmethod
    def __top(df: pd.DataFrame, category: str) -> pd.DataFrame:
        """Finds the top category (how many times an Artist, Track or Album was scrobbled) in the given dataframe and returns a new dataframe with them."""
        new_df = df.copy()

        if category == 'Track':
            new_df['Count'] = new_df.groupby(['Track', 'Artist']).transform('count')
            new_df = new_df.set_index('Count').drop_duplicates(['Track', 'Artist'])

            # sorting by count, then artist and then by track
            return new_df.iloc[ np.lexsort([new_df['Track'].str.upper(), new_df['Artist'].str.upper(), -new_df.index]) ]
        
        elif category == 'Album':
            new_df = new_df[ ~(new_df['Album'] == 'Last.fm Web Player') ]     # dropping the songs that were listened in Last.fm Web Player
            
            new_df['Count'] = new_df.groupby(['Album', 'Artist']).transform('count')
            new_df = new_df.set_index('Count').drop_duplicates(['Album', 'Artist']).drop('Track', axis='columns')

            # sorting by count, then artist and then by album
            return new_df.iloc[ np.lexsort([new_df['Album'].str.upper(), new_df['Artist'].str.upper(), -new_df.index]) ]

        elif category == 'Artist':
            new_df['Count'] = new_df.groupby('Artist').transform('count')['Album']
            new_df = new_df.set_index('Count').drop_duplicates('Artist').drop(['Track', 'Album'], axis='columns')

            # sorting by count and then by artist
            return new_df.iloc[ np.lexsort([new_df['Artist'].str.upper(), -new_df.index]) ]
        
        else:
            raise KeyError(category)


    def highlights_week(self, date: str) -> Dict[str, Dict[str, int]]:
        """
        Counts stats like the total and average daily scrobbles, total artists and albums of the current and last week.

        Paramaters:
            date: Desired date (YYYY-MM-DD).

        Returns:
            A dictionary with:
            {
                'Current Week': {
                    'Artists': int
                    'Albums': int
                    'Tracks': int
                    'Scrobbles': int
                    'Avarage Daily': int
                },

                'Last Week': {
                    'Artists': int
                    'Albums': int
                    'Tracks': int
                    'Scrobbles': int
                    'Avarage Daily': int
                }
            }
        """
        scrobbles_cur_week = self.top_by_week('Track', date).index.values.sum()
        tracks_cur_week = self.top_by_week('Track', date).value_counts('Track').sum()
        albums_cur_week = self.top_by_week('Album', date).value_counts('Album').sum()
        artists_cur_week = self.top_by_week('Artist', date).value_counts('Artist').sum()

        last_week = pd.Timestamp(date) - pd.Timedelta(7, 'D')

        scrobbles_last_week = self.top_by_week('Track', last_week).index.values.sum()
        tracks_last_week = self.top_by_week('Track', last_week).value_counts('Track').sum()
        albums_last_week = self.top_by_week('Album', last_week).value_counts('Album').sum()
        artists_last_week = self.top_by_week('Artist', last_week).value_counts('Artist').sum()

        return {
            'Current Week': {
                'Artists': artists_cur_week,
                'Albums': albums_cur_week,
                'Tracks': tracks_cur_week,
                'Scrobbles': scrobbles_cur_week,
                'Avarage Daily': round(scrobbles_cur_week / 7),
            },

            'Last Week': {
                'Artists': artists_last_week,
                'Albums': albums_last_week,
                'Tracks': tracks_last_week,
                'Scrobbles': scrobbles_last_week,
                'Avarage Daily': round(scrobbles_last_week / 7)
            }
        }

    
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