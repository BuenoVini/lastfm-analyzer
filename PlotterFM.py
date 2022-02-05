from AnalyzerFM import AnalyzerFM
import matplotlib.pyplot as plt # type: ignore
import pandas as pd # type: ignore
import os # type: ignore

class PlotterFM():
    """
    A plotter using matplotlib's methods to show the user's data in graphs.

    Public instance variables:
        None.

    Public methods:
        total_artists_year(): Shows a graph with the total number of artists listened that year by month.
        total_albums_year(): Shows a graph with the total number of albums listened that year by month.
        total_tracks_year(): Shows a graph with the total number of tracks listened that year by month.
        total_scrobbles_year(): Shows a graph with the total number of scrobbles listened that year by month.
        most_listened_artists(): Shows a graph with the total number of scrobbles of the most listened artist in each month of that year.
    """
    def __init__(self, user: str) -> None:
        """
        Constructs the analyzer object with the user's data to be used by the Plotter. 

        Parameters:
            user: Last.fm username

        Returns:
            None.
        """
        # setting the private attributes
        self.__analyzer = AnalyzerFM(user)
        self.__months_names = 'Jan Feb Mar Apr May Jun Jul Agu Sep Oct Nov Dec'.split()


    def __render_barh(self, data: pd.DataFrame, title: str, xlabel: str, ylabel: str,  save_it: bool, color: str='salmon') -> None:
        """Calls the barh() method from matplotlibs and customize it based upon the data passed."""
        # setting graph size
        plt.figure(figsize=(10, 5), facecolor='white')

        # setting graph title and labels
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)

        # displaying the scrobbles counts
        plt.barh(y=self.__months_names[::-1], width=data[::-1]['Count'], color=color)
        for index, value in enumerate(data[::-1]['Count']):
            plt.text(x=value+1, y=index-.2, s=str(value))

        # displaying the artist's name
        if 'Artist' in data.columns:
            for index, artist_name in enumerate(data[::-1]['Artist']):
                plt.text(x=5, y=index-.2, s=artist_name)

        # saving the graph if asked
        if save_it == True:
            if not os.path.isdir('results/'):
                os.mkdir('results/')
            plt.savefig(f'results/{title.replace(" ", "_").lower()}.png', facecolor='white')

        # displaying the graph
        plt.show()


    def total_artists_year(self, year: str, save_it: bool=False) -> None:
        """
        Displays a graph with the total count of artists scrobbled in each month of that year.

        Parameters:
            year: the desired year in 'YYYY' format.
            save_it: whether you wish to save the graph as am image or not.

        Returns:
            None.
        """
        # creating the dataframe with the total count of artists
        total_artists = pd.DataFrame( [self.__analyzer.highlights_of('year', f'{year}-{month+1}').total_artists for month, _ in enumerate(self.__months_names)], columns={'Count'} )

        # calling the renderer and displaying the graph to the user
        self.__render_barh(data=total_artists, title=f'Total Artists Listened in {year}', xlabel='Total Scrobbles', ylabel='Months', save_it=save_it)

    
    def total_albums_year(self, year: str, save_it: bool=False) -> None:
        """
        Displays a graph with the total count of albums scrobbled in each month of that year.

        Parameters:
            year: the desired year in 'YYYY' format.
            save_it: whether you wish to save the graph as am image or not.

        Returns:
            None.
        """
        # creating the dataframe with the total count of albums
        total_albums = pd.DataFrame( [self.__analyzer.highlights_of('year', f'{year}-{month+1}').total_albums for month, _ in enumerate(self.__months_names)], columns={'Count'} )

        # calling the renderer and displaying the graph to the user
        self.__render_barh(data=total_albums, title=f'Total Albums Listened in {year}', xlabel='Total Scrobbles', ylabel='Months', save_it=save_it)
        

    def total_tracks_year(self, year: str, save_it: bool=False) -> None:
        """
        Displays a graph with the total count of tracks scrobbled in each month of that year.

        Parameters:
            year: the desired year in 'YYYY' format.
            save_it: whether you wish to save the graph as am image or not.

        Returns:
            None.
        """
        # creating the dataframe with the total count of tracks
        total_tracks = pd.DataFrame( [self.__analyzer.highlights_of('year', f'{year}-{month+1}').total_tracks for month, _ in enumerate(self.__months_names)], columns={'Count'} )

        # calling the renderer and displaying the graph to the user
        self.__render_barh(data=total_tracks, title=f'Total Tracks in {year}', xlabel='Total Scrobbles', ylabel='Months', save_it=save_it)

    
    def total_scrobbles_year(self, year: str, save_it: bool=False) -> None:
        """
        Displays a graph with the total count of scrobbles in each month of that year.

        Parameters:
            year: the desired year in 'YYYY' format.
            save_it: whether you wish to save the graph as am image or not.

        Returns:
            None.
        """
        # creating the dataframe with the total count of scrobbles
        total_scrobbles = pd.DataFrame( [self.__analyzer.highlights_of('year', f'{year}-{month+1}').total_scrobbles for month, _ in enumerate(self.__months_names)], columns={'Count'} )

        # calling the renderer and displaying the graph to the user
        self.__render_barh(data=total_scrobbles, title=f'Total Scrobbles in {year}', xlabel='Total Scrobbles', ylabel='Months', save_it=save_it)


    def most_listened_artists(self, year: str, save_it: bool=False) -> None:
        """
        Displays a graph with the total count of scrobbles of the most listened artist in each month of that year.

        Parameters:
            year: the desired year in 'YYYY' format.
            save_it: whether you wish to save the graph as am image or not.

        Returns:
            None.
        """
        # creating the dataframe with the most listened artists
        top_artists = pd.DataFrame( [self.__analyzer.highlights_of('year', f'{year}-{month+1}').df_top_artist for month, _ in enumerate(self.__months_names)] ).reset_index(drop=True)

        # calling the renderer and displaying the graph to the user
        self.__render_barh(data=top_artists, title=f'Most Listened Artists in {year}', xlabel='Total Scrobbles', ylabel='Months', save_it=save_it, color='skyblue')
