from AnalyzerFM import AnalyzerFM
import matplotlib.pyplot as plt # type: ignore
import pandas as pd

class PlotterFM():
    def __init__(self, user: str) -> None:
        self.__analyzer = AnalyzerFM(user)
        self.__months_names = 'Jan Feb Mar Apr May Jun Jul Agu Sep Oct Nov Dec'.split()


    def __render_barh(self, data: pd.DataFrame, title: str, xlabel: str, ylabel: str, color: str='salmon') -> None:
        plt.figure(figsize=(10, 5))

        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

        plt.barh(y=self.__months_names[::-1], width=data[::-1]['Count'], color=color)
        for index, value in enumerate(data[::-1]['Count']):
            plt.text(x=value+1, y=index-.2, s=str(value))

        if 'Artist' in data.columns:
            for index, artist_name in enumerate(data[::-1]['Artist']):
                plt.text(x=5, y=index-.2, s=artist_name)

        plt.show()


    def total_artists_year(self, year: str) -> None:
        total_artists = pd.DataFrame( [self.__analyzer.highlights_of('year', f'{year}-{month+1}').total_artists for month, _ in enumerate(self.__months_names)], columns={'Count'} )

        self.__render_barh(data=total_artists, title=f'Total Artists Listened in {year}', xlabel='Total Scrobbles', ylabel='Months')

    
    def total_albums_year(self, year: str) -> None:
        total_albums = pd.DataFrame( [self.__analyzer.highlights_of('year', f'{year}-{month+1}').total_albums for month, _ in enumerate(self.__months_names)], columns={'Count'} )

        self.__render_barh(data=total_albums, title=f'Total Albums Listened in {year}', xlabel='Total Scrobbles', ylabel='Months')
        

    def total_tracks_year(self, year: str) -> None:
        total_tracks = pd.DataFrame( [self.__analyzer.highlights_of('year', f'{year}-{month+1}').total_tracks for month, _ in enumerate(self.__months_names)], columns={'Count'} )

        self.__render_barh(data=total_tracks, title=f'Total Scrobbles in {year}', xlabel='Total Scrobbles', ylabel='Months')

    
    def total_scrobbles_year(self, year: str) -> None:
        total_scrobbles = pd.DataFrame( [self.__analyzer.highlights_of('year', f'{year}-{month+1}').total_scrobbles for month, _ in enumerate(self.__months_names)], columns={'Count'} )

        self.__render_barh(data=total_scrobbles, title=f'Total Scrobbles in {year}', xlabel='Total Scrobbles', ylabel='Months')


    def most_listened_artists(self, year: str) -> None:
        top_artists = pd.DataFrame( [self.__analyzer.highlights_of('year', f'{year}-{month+1}').df_top_artist for month, _ in enumerate(self.__months_names)] ).reset_index(drop=True)

        self.__render_barh(data=top_artists, title=f'Most Listened Artists in {year}', xlabel='Total Scrobbles', ylabel='Months', color='skyblue')
