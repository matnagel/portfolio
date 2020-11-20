from portfolio import *

import numpy
import unittest

def constructTestISIN(isin):
    data = {isin:'Test Company'}
    return pd.DataFrame.from_dict(data, orient='index', columns = ['name'])

def constructConstantHistory(isin, price, times):
    coldata = {'isin' : [isin for _ in times],
            'last' : [price for _ in times]}
    return pd.DataFrame(coldata, index=times)

def constructBullHistory(isin, times):
    prices = []
    for i in range(len(times)):
        prices.append(10+i)
    coldata = {'isin' : [isin for _ in times],
            'last' : prices}
    return pd.DataFrame(coldata, index=times)


def constructNullTransactions(isin, times):
    coldata = {'amount' : [0 for _ in times],
            'spent' : [ 0 for _ in times],
            'isin' : [isin for _ in times]
            }
    return pd.DataFrame(coldata, index=times)

def constructBuyAndHoldTransactions(isin, times, amount, spent):
        coldata = {'amount' : [0 for _ in times],
                'spent' : [ 0 for _ in times],
                'isin' : [isin for _ in times]
                }
        coldata['amount'][0] = amount
        coldata['spent'][0] = spent
        return pd.DataFrame(coldata, index=times)

def constructBuyAndSellTransactions(isin, times):
        coldata = {'amount' : [0 for _ in times],
                'spent' : [ 0 for _ in times],
                'isin' : [isin for _ in times]
                }
        coldata['amount'][10] = 10
        coldata['spent'][10] = 200

        coldata['amount'][15] = -5
        coldata['spent'][15] = -25*5

        coldata['amount'][25] = -5
        coldata['spent'][25] = -35*5
        return pd.DataFrame(coldata, index=times)


class TestPortfolioTWR(unittest.TestCase):
    def testNullTransaction(self):
        isin = '0506070'
        times = pd.date_range('2020-01-01', periods=20, freq='D')
        env = Environment(constructTestISIN(isin),
                constructConstantHistory(isin, 10, times))
        trans = constructNullTransactions(isin, times)
        stockPos = StockPosition(env, isin, trans)
        self.assertTrue(numpy.isnan(stockPos.getGainAtTimes(times).iloc[-1]))
    def testBuyAndHoldTransaction(self):
        isin = '0506070'
        times = pd.date_range('2020-01-01', periods=20, freq='D')
        env = Environment(constructTestISIN(isin),
                constructConstantHistory(isin, 10, times))
        trans = constructBuyAndHoldTransactions(isin, times, 1, 10)
        stockPos = StockPosition(env, isin, trans)
        self.assertEqual(stockPos.getGainAtTimes(times).iloc[-1],1)

        trans = constructBuyAndHoldTransactions(isin, times, 10, 10)
        stockPos = StockPosition(env, isin, trans)
        self.assertEqual(stockPos.getGainAtTimes(times).iloc[-1],10)
        self.assertEqual(stockPos.getValueAtTimes(times).iloc[-1],100)

        env = Environment(constructTestISIN(isin),
                constructBullHistory(isin, times))
        trans = constructBuyAndHoldTransactions(isin, times, 1, 10)
        stockPos = StockPosition(env, isin, trans)
        self.assertEqual(stockPos.getGainAtTimes(times).iloc[-1],2.9)
    def testBuyAndSellTransaction(self):
        isin = '0506070'
        times = pd.date_range('2020-01-01', periods=30, freq='D')
        env = Environment(constructTestISIN(isin),
                constructBullHistory(isin, times))
        trans = constructBuyAndSellTransactions(isin, times)
        stockPos = StockPosition(env, isin, trans)
        self.assertEqual(stockPos.getSpentAtTimes(times).iloc[-1],-100)

if __name__ == '__main__':
    unittest.main()
