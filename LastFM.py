import time
import datetime
import requests
from typing import Dict
from dotenv import dotenv_values

class LastFM:
    def __init__(self) -> None:
        self.__config = dotenv_values('.env')


    def __get(self, payload: Dict[str, str]) -> requests.models.Response:
        url = 'http://ws.audioscrobbler.com/2.0'                # the API root URL location
        my_header = {'User-Agent': 'lastfm-analyzer'}           # using an identifiable User-Agent header as noted in Last.fm docs

        # verifying if the returned value was not None (i.e. a str) beacuse dotenv_values() returns Optional[str]
        if self.__config['API_KEY'] is not None:
            payload['api_key'] = self.__config['API_KEY']       # adding the API KEY to the payload
            payload['format'] = 'json'                          # setting the format of the response to json

            return requests.get(url, headers=my_header, params=payload) # sending the request and returning its response
        else:
            raise Exception("dotenv_values() returned None")


    @staticmethod
    def __date_seconds(date_input: str) -> str:
        """
        converts the date_input string (YYYY-MM-DD) to the Unix Timestamp notation
        """
        date = time.strptime(date_input, "%Y-%m-%d")      # converts the date string to struct_time

        return f"{(datetime.date(date.tm_year, date.tm_mon, date.tm_mday) - datetime.date(1970, 1, 1)).total_seconds():.0f}"    # instead of returning a float (e.g., 629510400.0), it returns a string (e.g., '629510400')
            

    def get_recent_tracks(self, user: str, from_date: str, to_date: str, limit: int = 50, page: int = 1) -> requests.models.Response:
        """
        from_date: "YYYY-MM-DD" meaning year-month-day. start from this day
        to_date: "YYYY-MM-DD" meaning year-month-day. stop before this day (open)
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
    print( api.get_recent_tracks('Vini_Bueno', '2019-01-01', '2020-01-01') )