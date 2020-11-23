import pandas as pd
import datetime as dt

import toolz

class HasSpending:
    def getGainAtTimes(self, times):
        return self.getValueAtTimes(times) / self.getSpentAtTimes(times)
    def getReturnAtTimes(self, times):
        return self.getValueAtTimes(times) - self.getSpentAtTimes(times)

class Stock():
    def __init__(self, env, isin):
        self.isin = isin
        self.prices = env.lookupPrices(isin)
        self.name = env.lookupName(isin)
    def getValueAtTimes(self, times):
        values = self.prices.reindex(times, method='ffill')
        return values
    def learnPricesFromTransactions(self, transactions):
        tprice = transactions['spent'] / transactions['amount']
        tprice = tprice[tprice > 0]
        self.prices = pd.concat([self.prices, tprice]).sort_index()
        self.prices = self.prices.groupby(level=0).last()
    def __str__(self):
        return self.name

class StockPosition(HasSpending):
    def __init__(self, env, isin, transactions):
        self.stock = Stock(env, isin)
        transactions = transactions[transactions['isin'] == isin]
        self.stock.learnPricesFromTransactions(transactions)
        self.amount = transactions['amount'].cumsum()
        self.amount = self.amount.groupby(level=0).last()
        self.spent = transactions['spent'].cumsum()
        self.spent = self.spent.groupby(level=0).last()
    def getValueAtTimes(self, times):
        amount = self.getAmountAtTimes(times)
        valueAtTimes = self.stock.getValueAtTimes(times)*amount
        valueAtTimes[amount == 0] = 0
        return valueAtTimes
    def getAmountAtTimes(self, times):
        amountAtTimes = self.amount.reindex(times, method='ffill', fill_value = 0)
        return amountAtTimes
    def getSpentAtTimes(self,times):
        spentAtTimes = self.spent.reindex(times, method='ffill', fill_value = 0)
        return spentAtTimes
    def getISIN(self):
        return self.stock.isin
    def __str__(self):
        return f"Position in {self.stock.name} has spent {self.spent.iloc[-1]}"

class StockPortfolio(HasSpending):
    def __init__(self, holdings):
        self.holdings = holdings
    def getValueAtTimes(self, times):
        valueDict = self.mapHoldings(lambda p : p.getValueAtTimes(times))
        return sum(valueDict.values())
    def mapHoldings(self, f):
        return toolz.valmap(f, self.holdings)
    def getSpentAtTimes(self, times):
        spentDict = self.mapHoldings(lambda p : p.getSpentAtTimes(times))
        return sum(spentDict.values())
    def getPercentagesAtTimes(self, times):
        totalValue = self.getValueAtTimes(times)
        perc = self.mapHoldings(lambda p : p.getValueAtTimes(times) / totalValue)
        return perc
    @staticmethod
    def fromTransactions(env, transactions):
        holdings = {}
        for isin in transactions['isin'].unique():
            pos = StockPosition(env, isin, transactions)
            holdings[isin] = pos
        return StockPortfolio(holdings)

class Environment:
    def __init__(self, isins, history):
        self.isins = isins
        self.history = history
    def truncate(self):
        curisin = self.isins.index.values
        self.history = self.history[self.history['isin'].isin(curisin)]
    def writeBack(self):
        self.history.to_csv('data/history.csv')
    def lookupPrices(self, isin):
        return self.history[self.history['isin'] == isin]['last']
    def lookupName(self, isin):
        return self.isins.loc[isin]['name']
    @staticmethod
    def withStandardPaths():
        isins = pd.read_csv('data/isin.csv', index_col='isin')
        history = pd.read_csv('data/history.csv', parse_dates=['date'], index_col='date')
        return Environment(isins, history)

class SpendingStats:
    def __init__(self, flowable):
        self.times = pd.date_range(end=pd.datetime.now(), periods=1, freq='D')
        self.value = flowable.getValueAtTimes(self.times).iloc[-1]
        self.gain = flowable.getGainAtTimes(self.times).iloc[-1]
        self.spent = flowable.getSpentAtTimes(self.times).iloc[-1]
    def getValue(self):
        return self.value
    def getGain(self):
        return self.gain
    def getSpent(self):
        return self.spent
    def getReturn(self):
        return self.value - self.spent

class PositionStats(SpendingStats):
    def __init__(self, position):
        SpendingStats.__init__(self, position)
        self.amount = position.getAmountAtTimes(self.times).iloc[-1]
    def getAmount(self):
        return self.amount

class PortfolioStats(SpendingStats):
    def __init__(self, portfolio):
        SpendingStats.__init__(self, portfolio)
        self.percentageDict = toolz.valmap(
                lambda pvalue: pvalue.iloc[-1],
                portfolio.getPercentagesAtTimes(self.times))
    def getPercentageDict(self):
        return self.percentageDict

class PortfolioTable:
    def __init__(self, portfolio):
        self.portfolio = portfolio
    def getOverviewTable(self):
        statDict = self.portfolio.mapHoldings(lambda p :
                [p.stock.name,
                 SpendingStats(p).getGain()-1,
                 SpendingStats(p).getValue(),
                 PositionStats(p).getAmount(),
                 PortfolioStats(self.portfolio).getPercentageDict()[p.getISIN()]
                ])
        statDict = toolz.itemfilter(lambda item: item[1][-1] > 0, statDict)
        return pd.DataFrame.from_dict(statDict,
                columns=['Name', 'Gain', 'Value', 'Amount', 'Percentage'], orient='index')

# env = Environment.withStandardPaths()
# transactions = pd.read_csv('data/portfolio.csv', parse_dates=['date'], index_col='date')
# portfolio = StockPortfolio.fromTransactions(env,transactions)
# table = PortfolioTable(portfolio)
