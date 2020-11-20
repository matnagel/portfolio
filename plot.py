from pandas_datareader import data
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from portfolio import *

class PortfolioPlot:
    def __init__(self, portfolio, days):
        self.index = pd.date_range(end=pd.datetime.now(), periods=days, freq='D')
        self.returnSeries = portfolio.getGainAtTimes(self.index)
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
