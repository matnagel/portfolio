from pandas_datareader import data
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from portfolio import *

class PortfolioPlot:
    def __init__(self, port):
        self.index = pd.date_range(end=pd.datetime.now(), periods=60, freq='D')
        self.returnSeries = port.bigtable['totalValueOfPortfolio'] / port.bigtable['spentOnPortfolio']

        #Remove duplicates
        self.returnSeries = self.returnSeries[~self.returnSeries.index.duplicated(keep='first')]
        self.returnSeries = self.returnSeries.reindex(self.index, method='ffill')
    def plot(self):
        self.returnSeries.plot()
        plt.title('Portfolio gain')
        plt.show()
    def getFigure(self):
        fig = Figure()
        axes = fig.add_subplot(111)
        self.returnSeries.plot(ax=axes)
        axes.plot()
        return fig
