from portfolio import *
from plot import *

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk

#from matplotlib.backends.backend_gtk3cairo import (
#    FigureCanvasGTK3Cairo as FigureCanvas)
from matplotlib.backends.backend_gtk3agg import (
    FigureCanvasGTK3Agg as FigureCanvas)

class Handler:
    def onExit(self, button):
        Gtk.main_quit()

def percentageFormater(treeView, cell, model, iter, userdata):
    (columnNumber, formatString) = userdata
    val = model.get(iter, columnNumber)[0]
    cell.set_property("text", formatString.format(val))

class PandasViewer():
    def __init__(self, df, viewer, columnFormats = {}):
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

            if col in columnFormats:
                column.set_cell_data_func(renderer, percentageFormater,
                        (i, columnFormats[col]))
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

env = Environment.withStandardPaths()

builder = Gtk.Builder()
builder.add_from_file("gui.glade")
builder.connect_signals(Handler())

df = env.isins.reset_index()
viewer = builder.get_object("basicStockView")
isinViewer = PandasViewer(df, viewer)

transactions = pd.read_csv('data/portfolio.csv', parse_dates=['date'], index_col='date')
portfolio = StockPortfolio.fromTransactions(env,transactions)
cur = SpendingStats(portfolio)

stats = PortfolioTable(portfolio).getOverviewTable()
viewer = builder.get_object("portfolioView")
columnFormats = {'Gain':"{:.2%}",
        'Percentage':"{:.2%}",
        'Value':"{:0.2f}",
        'Amount' : "{:0.2f}"}
portfolioViewer = PandasViewer(stats, viewer, columnFormats)

performanceLabel = builder.get_object("PortfolioNumbers")
cgain = cur.getGain()
creturn = cur.getReturn()
cvalue = cur.getValue()
performanceLabel.set_text(f"Gain: {cgain:.3f}, "
        f"Return: {creturn:.2f}, Value: {cvalue:.0f}")

contentBox = builder.get_object("contentBox")
pplot = PortfolioPlot(portfolio, 360)
canvas = FigureCanvas(pplot.getFigure())
canvas.set_size_request(400, 400)
contentBox.add(canvas)

window = builder.get_object("basicStockEditor")
window.show_all()

Gtk.main()
