from AnalyzerFM import AnalyzerFM
import matplotlib.pyplot as plt # type: ignore
import numpy as np

class PlotterFM():
    def __init__(self, user: str) -> None:
        self.__analyzer = AnalyzerFM(user)
        self.__months_names = 'Jan Feb Mar Apr May Jun Jul Agu Sep Oct Nov Dec'.split()


    def __render_barh(self, data: np.ndarray, title: str, xlabel: str, ylabel: str) -> None:
        plt.figure(figsize=(10, 5))

        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

        plt.barh(y=self.__months_names[::-1], width=data[::-1], color='salmon')
        for index, value in enumerate(data[::-1]):
            plt.text(x=value+1, y=index-.2, s=str(value))
        
        plt.show()


    def total_artists_year(self, year: str) -> None:
        total_artists = np.array( [self.__analyzer.highlights_of('year', f'{year}-{month}').total_artists for month in range(1, 13)] )

        self.__render_barh(data=total_artists, title=f'Total Artists Listened in {year}', xlabel='Total Scrobbles', ylabel='Months')
        

    def total_scrobbles_year(self, year: str) -> None:
        total_scrobbles = np.array( [self.__analyzer.highlights_of('year', f'{year}-{month}').total_scrobbles for month in range(1, 13)] )

        self.__render_barh(data=total_scrobbles, title=f'Total Scrobbles in {year}', xlabel='Total Scrobbles', ylabel='Months')
        
        