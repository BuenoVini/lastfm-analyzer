import requests
from time import strptime
from datetime import date
from typing import Dict
from dotenv import dotenv_values

class LastFM:
    """
    An API to connect and fetch data from the Last.fm servers.

    Public instance variables:
        None.

    Public methods:
        get_recent_tracks(): Gets the user's recent played tracks within the interval [from_date, to_date).
    """
    def __init__(self) -> None:
        """Constructs all the necessary attributes for the LastFM object, such as the API keys."""
        self.__config = dotenv_values('.env')


    def __get(self, payload: Dict[str, str]) -> requests.models.Response:
        """Returns the response from the Last.fm servers."""
        url = 'http://ws.audioscrobbler.com/2.0'                # the API root URL location
        my_header = {'User-Agent': 'lastfm-analyzer'}           # using an identifiable User-Agent header as noted in Last.fm docs

        # verifying if the returned value was not None (i.e. a str) beacuse dotenv_values() returns Optional[str]
        if self.__config['API_KEY'] is not None:
            payload['api_key'] = self.__config['API_KEY']       # adding the API KEY to the payload
            payload['format'] = 'json'                          # adding the format of the response as json

            return requests.get(url, headers=my_header, params=payload) # sending the request and returning its response
        else:
            raise Exception("dotenv_values() returned None")


    @staticmethod
    def __date_seconds(date_input: str) -> str:
        """Converts the date_input string ('YYYY-MM-DD') to the Unix Timestamp notation."""
        date_output = strptime(date_input, "%Y-%m-%d")      # converts the date string to struct_time

        return f"{(date(date_output.tm_year, date_output.tm_mon, date_output.tm_mday) - date(1970, 1, 1)).total_seconds():.0f}"    # instead of returning a float (e.g., 629510400.0), it returns a string (e.g., '629510400')
            

    def get_recent_tracks(self, user: str, from_date: str, to_date: str, limit: int = 50, page: int = 1) -> requests.models.Response:
        """
        Gets the user's recent played tracks within the interval [from_date, to_date).

        Parameters:
            user: Last.fm username
            from_date: String ('YYYY-MM-DD') to start from this day (closed interval).
            to_date: String ('YYYY-MM-DD') to stop before this day (opened interval).
            limit: The number of results to fetch per page. Defaults to 50. Maximum is 200.
            page: The page number to fetch. Defaults to first page (1).

        Returns:
            The server response with the user's recent played tracks
        """
        payload = {
            'method': 'user.getrecenttracks', 
            'user': user,
            'from': self.__date_seconds(from_date), 
            'to': self.__date_seconds(to_date),
            'limit': str(limit),
            'page': str(page)
        }

        return self.__get(payload)


if __name__ == '__main__':
    api = LastFM()
    response = api.get_recent_tracks('Vini_Bueno', '2019-01-01', '2020-01-01')
    print( response.status_code )
    print( response.json() )