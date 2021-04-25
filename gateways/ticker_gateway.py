import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

TRADING_DAYS = 252

class TickerGateway(object):
    @staticmethod
    def get_ticker_info(ticker_name):
            t = yf.Ticker(ticker_name)
            return t.info

    @staticmethod
    def calculate_volatility(ticker, timeframe='1y'):
        t = yf.Ticker(ticker)
        h = t.history(period=timeframe)
        h.sort_index(ascending=False, inplace=True)
        x = (np.log(h['Close'] / h['Close'].shift(-1)))
        x.dropna()
        std = np.std(x)
        s = std * TRADING_DAYS ** 0.5
        fig, ax = plt.subplots(1, 1, figsize=(5, 4))
        n, bins, patches = ax.hist(x.values, bins=50, alpha=0.65, color='blue')
        y = ((1 / (np.sqrt(2 * np.pi) * std)) *
             np.exp(-0.5 * (1 / std * (bins - x.mean())) ** 2))
        ax.plot(bins, y, '--', color="orange")
        ax.set_xlabel('log return of stock price')
        ax.set_ylabel('frequency of log return')
        ax.set_title('Historical Volatility for {}'.format(t.info['longName']))
        x_corr = ax.get_xlim()
        y_corr = ax.get_ylim()
        header = y_corr[1] / 5
        y_corr = (y_corr[0], y_corr[1] + header)
        ax.set_ylim(y_corr[0], y_corr[1])
        x = x_corr[0] + (x_corr[1] - x_corr[0]) / 30
        y = y_corr[1] - (y_corr[1] - y_corr[0]) / 15
        y_ = y_corr[1] - (y_corr[1] - y_corr[0]) / 7
        ax.text(x, y, 'Anualized Volatility: ' + str(np.round(s * 100, 1)) + '%', fontsize=11, fontweight='bold')
        ax.text(x, y_, 'Mean Return Value:' + str(np.round(x.mean(), 7)), fontsize=11, fontweight='bold')
        fig.tight_layout()
        return fig

    @staticmethod
    def plot_volatility(ticker):
        ticker = yf.Ticker(ticker)
        t = ticker.history(period='10y')
        returns = np.log(t['Close'] / t['Close'].shift(1))
        returns.dropna()
        volatility = returns.rolling(window=TRADING_DAYS).std() * np.sqrt(TRADING_DAYS)
        volatility.fillna(0, inplace=True)
        fig = plt.figure(figsize=(5, 4))
        ax1 = fig.add_subplot(1, 1, 1)
        volatility.plot(ax=ax1)
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Volatility')
        ax1.set_title('Annualized volatility for {}'.format(ticker.info['longName']))
        return fig


