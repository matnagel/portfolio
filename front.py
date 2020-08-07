from portfolio import *
from plot import *

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

from matplotlib.backends.backend_gtk3cairo import (
    FigureCanvasGTK3Cairo as FigureCanvas)

class Handler:
    def onExit(self, button):
        Gtk.main_quit()

class PandasViewer():
    def __init__(self, df, viewer):
        self.df = df
        self.store = Gtk.ListStore()
        ctypes = self.extractColumnTypes(df)
        self.store.set_column_types(ctypes)
        self.viewer = viewer

        # fill it with your data
        for row in df.itertuples(index=False):
            self.store.append(list(row))
        self.viewer.set_model(self.store)

        # Create and append columns
        for i, col in enumerate(df.columns, start=0):
            renderer = Gtk.CellRendererText() #editable=True)
            # renderer.connect("edited", self.editCell, i)
            column = Gtk.TreeViewColumn(col, renderer, text=i)
            column.set_resizable(True)
            self.viewer.append_column(column)

    def extractColumnTypes(self, df):
        columnTypes = []
        for name in df:
            if df[name].dtype.name == 'object':
                columnTypes.append(str)
            elif df[name].dtype.name == 'float64':
                columnTypes.append(float)
            else:
                raise Exception("Unknown DType for column:" ++ name)
        return columnTypes

    # def editCell(self, renderer, pathString, newText, cellNum):
    #     if len(newText) > 0:
    #         iter = self.store.get_iter_from_string(pathString)
    #         if iter:
    #             self.store.set(iter, cellNum, newText)
    #             path = self.store.get_path(iter)
    #             row = path.get_indices()[0]
    #             self.df.iat[row, cellNum] = newText
    #             print(df)

env = Environment()

builder = Gtk.Builder()
builder.add_from_file("gui.glade")
builder.connect_signals(Handler())

df = env.isins.reset_index()
viewer = builder.get_object("basicStockView")
isinViewer = PandasViewer(df, viewer)

pdata = pd.read_csv('data/portfolio.csv', parse_dates=['date'], index_col='date')
portfolio = Portfolio(env, pdata)
stats = portfolio.status()
viewer = builder.get_object("portfolioView")
portfolioViewer = PandasViewer(stats, viewer)

contentBox = builder.get_object("contentBox")
pplot = PortfolioPlot(portfolio)
canvas = FigureCanvas(pplot.getFigure())
canvas.set_size_request(400, 400)
contentBox.add(canvas)

performanceLabel = builder.get_object("PortfolioNumbers")
gains = portfolio.getGain()
returns = portfolio.getReturn()
performanceLabel.set_text(f"Gain: {gains:.3f}, Return: {returns:.2f}")

window = builder.get_object("basicStockEditor")
window.show_all()

Gtk.main()
