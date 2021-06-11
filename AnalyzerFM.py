from typing import List
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
        df: dataframe with all scrobbles information of that user.

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
            
            # append current response to pages
            pages.append(response.json())

            # verifying if the current page does not exceed the max page number... if it does (last one), break the loop
            if current_page < int(response.json()['recenttracks']['@attr']['totalPages']):
                # verifying if the response came from the server (and not from the cache)
                if not getattr(response, 'from_cache', False):
                    print(response.status_code, current_page, response.json()['recenttracks']['@attr']['totalPages'])
                    sleep(0.25)
                
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



    @staticmethod
    def __top(df: pd.DataFrame, category: str) -> pd.DataFrame:
        """Finds the top category (Artist, Album or Track) in the given dataframe and returns a new dataframe with them."""
        # creating a new dataframe with each track's frequency
        counted_df = df.copy()
        counted_df['Count'] = counted_df.groupby(by=['Artist', 'Track']).transform('count')
        counted_df = counted_df.set_index(['Artist', 'Album', 'Track']).sort_index()
        counted_df = counted_df[ ~counted_df.index.get_level_values('Track').duplicated() ]

        if category == 'Track':
            return counted_df.groupby(level=['Artist', 'Album', 'Track']).sum().sort_values('Count', ascending=False)
        
        elif category == 'Album':
            return counted_df.groupby(level=['Artist', 'Album']).sum().sort_values('Count', ascending=False)

        elif category == 'Artist':
            return counted_df.groupby(level='Artist').sum().sort_values('Count', ascending=False)
        
        else:
            raise KeyError(category)



    def top_by_week(self, category: str, year: int, month: int, day: int) -> pd.DataFrame:
        """
        Finds the top category (Artist, Album or Track) in the period of one week

        Parameters:
            category: can be either 'Artist', 'Track' or 'Album'
            year: desired year (YYYY)
            month: desired month (MM)
            day: desired day (DD)

        Returns:
            A list with the top category for the period of one week
        """
        current_week = pd.Timestamp(f"{year}-{month}-{day+1}")
        last_week = current_week - pd.Timedelta(7, 'D')

        return self.__top(self.df.loc[current_week:last_week], category)



    def top_by_month(self, category: str, year: int, month: int) -> pd.DataFrame:
        """
        Finds the top category (Artist, Album or Track) of a specif month of the given year

        Parameters:
            category: can be either 'Artist', 'Track' or 'Album'
            year: desired year (YYYY)
            month: desired month (MM)

        Returns:
            A list with the top category for the given month
        """
        return self.__top(self.df.loc[f'{year}-{month}'], category)



    def top_by_year(self, category: str, year: int) -> pd.DataFrame:
        """
        Finds the top category (Artist, Album or Track) of the whole year

        Parameters:
            category: can be either 'Artist', 'Track' or 'Album'
            year: desired year (YYYY)

        Returns:
            A list with the top category for the given year
        """
        return self.__top(self.df.loc[f'{year}'], category)




if __name__ == '__main__':
    analyzer = AnalyzerFM('Vini_Bueno')
    # for month in range(1, 6):
    #     print(f"\n2021-{month}", analyzer.top_by_month('Artist', 2021, month)[0:10], sep='\n')

    for year in [2018, 2019, 2020, 2021]:
        print(f"\n{year}", analyzer.top_by_year('Track', year).head(), sep='\n')

    # print("\nLast week:", analyzer.top_by_week('Track', 2021, 6, 3).head(), sep='\n')