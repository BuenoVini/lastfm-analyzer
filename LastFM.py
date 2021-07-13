import requests
from datetime import datetime
from datetime import date
from time import mktime, localtime, gmtime
from typing import Dict, Final
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
        """Constructs all the necessary attributes for the LastFM object, such as the API keys and the time zone offset."""
        self.__config = dotenv_values('.env')
        self.__timezone_offset: Final = int( (mktime(localtime()) - mktime(gmtime())) / 3600 )


    @property
    def timezone_offset(self) -> int:
        """A getter method for the timezone_offset attribute."""
        return self.__timezone_offset
    

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


    def __date_seconds(self, date_input: str) -> int:
        """Converts the date_input string ('YYYY-MM-DD') to the Unix Timestamp notation. The return value is in UTC time zone but taking the user's time zone into consideration."""
        # converts the date string to datetime
        date_output = datetime.strptime(date_input, "%Y-%m-%d")

        # calculating the Unix Timestamp value (e.g., 629510400) in UTC
        local_seconds = (date(date_output.year, date_output.month, date_output.day) - date(1970, 1, 1)).total_seconds()

        # returning the UTC value but with the user's time zone into account. e.g.:
        # from 629510400: Dec 13 1989 00:00:00 (UTC) == Dec 12 1989 21:00:00 (local -3 UTC)
        # to 629521200: Dec 13 1989 03:00:00 (UTC) == Dec 13 1989 00:00:00 (local -3 UTC)
        return int(local_seconds) - self.__timezone_offset*3600
            

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
        # creating the payload message to send to the Last.fm servers
        payload = {
            'method': 'user.getrecenttracks', 
            'user': user,
            'from': str(self.__date_seconds(from_date)), 
            'to': str(self.__date_seconds(to_date) - 1),    # instead of 00:00:00, it is desired 23:59:59
            'limit': str( max(1, min(limit, 200)) ),
            'page': str(page)
        }

        return self.__get(payload)


if __name__ == '__main__':
    api = LastFM()
    response = api.get_recent_tracks('Vini_Bueno', '2019-01-01', '2020-01-01', limit=400)
    print( response.status_code )
    # print( response.json() )