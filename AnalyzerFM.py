from time import sleep
from LastFM import LastFM
from datetime import date
from sys import exit
import requests_cache # type: ignore
import pandas as pd # type: ignore

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

        requests_cache.install_cache('demo_cache')      # caching the get response in cache.sqlite for faster performance

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
            'Song': [ scrobble['name'] for page in pages for scrobble in page['recenttracks']['track'] ],
            'Album': [ scrobble['album']['#text'] for page in pages for scrobble in page['recenttracks']['track'] ],
            'Date': [ scrobble['date']['#text'] for page in pages for scrobble in page['recenttracks']['track'] ]
        })

    
    def top_artists(self, start: int = 0, stop: int = -1) -> pd.DataFrame:
        return self.df['Artist'].value_counts().iloc[start:stop]


if __name__ == '__main__':
    analyzer = AnalyzerFM('Vini_Bueno')
    # print(analyzer.df)
    print(analyzer.top_artists(stop=20))