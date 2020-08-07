import pandas as pd
import datetime as dt

class Environment:
    def __init__(self):
        self.isins = pd.read_csv('data/isin.csv', index_col='isin')
        self.history = pd.read_csv('data/history.csv', parse_dates=['date'], index_col='date')
    def truncate(self):
        curisin = self.isins.index.values
        self.history = self.history[self.history['isin'].isin(curisin)]
    def writeBack(self):
        self.history.to_csv('data/history.csv')

class Portfolio:
    def __init__(self, env, pf):
        self.bigtable = pd.concat([env.history,pf],sort=False)[['isin','last','amount','spent']]
        self.bigtable.sort_index(inplace=True)
        self.bigtable.rename(columns={'amount':'transactionAmount', 'last':'currentPriceOfStock', 'spent':'transactionSpent'}, inplace=True)
        self.bigtable = self.bigtable.join(env.isins,on='isin')

        self.bigtable['transactionSpent'].fillna(0, inplace=True)
        self.bigtable['transactionAmount'].fillna(0, inplace=True)
        self.bigtable['amountOfStock'] = self.bigtable.groupby('isin')['transactionAmount'].transform(pd.Series.cumsum)
        self.bigtable['spentOnStock'] = self.bigtable.groupby('isin')['transactionSpent'].transform(pd.Series.cumsum)
        self.bigtable['spentPerStock'] = self.bigtable['spentOnStock'] / self.bigtable['amountOfStock']
        self.bigtable['currentPriceOfStock'] = self.bigtable.groupby('isin')['currentPriceOfStock'].transform(lambda x: x.fillna(method='ffill'))
        self.bigtable['valueOfStock'] = self.bigtable['currentPriceOfStock']*self.bigtable['amountOfStock']
        self.bigtable['gainOnStock'] = (self.bigtable['valueOfStock'] - self.bigtable['spentOnStock']) / self.bigtable['spentOnStock']
        self.bigtable['spentOnPortfolio'] = self.bigtable['transactionSpent'].cumsum()
        self.bigtable['totalValueOfPortfolio'] = self.computeTotalValueColumn(self.bigtable)
        self.bigtable['percentageOfPortfolio'] = self.bigtable['valueOfStock'] / self.bigtable['totalValueOfPortfolio']

    def computeTotalValueColumn(self, df):
        lastSeenValue = dict()
        arr = []
        for index, row in df.iterrows():
            val = row['valueOfStock']
            if pd.notna(val):
                lastSeenValue[row['isin']] = row['valueOfStock']
            arr.append(sum(lastSeenValue.values()))
        self.totalValue = sum(lastSeenValue.values())
        return pd.Series(arr, index=df.index)

    def status(self):
        stat = self.bigtable.groupby('isin').last()[['name','gainOnStock', 'currentPriceOfStock','amountOfStock','spentOnStock','valueOfStock','percentageOfPortfolio']]
        return stat[stat['amountOfStock'] > 0]
    def report(self):
        stat = self.bigtable.groupby('isin').last()[['name', 'gainOnStock', 'percentageOfPortfolio', 'spentPerStock', 'amountOfStock']]
        stat = stat[stat['amountOfStock'] > 0]
        stat = stat[['name', 'percentageOfPortfolio', 'spentPerStock']]
        for index, row in stat.iterrows():
            print(f"{row['name']:>20} {row['percentageOfPortfolio']:>5.1%} @{row['spentPerStock']:.2f}")

    def getGain(self):
        return self.totalValue / self.bigtable['spentOnPortfolio'].iloc[-1]
    def getReturn(self):
        return self.totalValue - self.bigtable['spentOnPortfolio'].iloc[-1]

env = Environment()
pf = pd.read_csv('data/portfolio.csv', parse_dates=['date'], index_col='date')
port = Portfolio(env,pf)
