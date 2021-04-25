import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging
import requests
import ftplib
import json
import time
import threading
import sqlite3

from io import BytesIO

logger = logging.getLogger('financial_analyst.spikes.playground')
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel((logging.DEBUG))

TRADING_DAYS = 252

def get_all_tsx_tickers():
    resp = requests.get('https://www.tsx.com/json/company-directory/search/tsx/^*')
    raw = json.loads(resp.text)
    tsx_tickers = [row['symbol'] for row in raw['results']]
    return tsx_tickers


def get_all_tickers():
    agg_file = BytesIO()
    ftp = ftplib.FTP("ftp.nasdaqtrader.com")
    ftp.login("anonymous", "anonymous")
    ftp.cwd('SymbolDirectory')
    ftp.retrbinary('RETR nasdaqlisted.txt', agg_file.write)
    ftp.retrbinary('RETR otherlisted.txt', agg_file.write)
    ftp.close()
    agg_file.seek(0)
    csv = pd.read_csv(agg_file, sep="|")
    agg_file.close()
    tickers = [q for q in csv['Symbol']][:-1]
    return tickers


def generate_tsx_info():
    ticker_list = []
    workers = []
    batch_size = 10
    tsx_tickers = ['{}.to'.format(t) for t in get_all_tsx_tickers()]
    for i in range(0, len(tsx_tickers), batch_size):
        batch = tsx_tickers[i:i + batch_size]
        for tick in batch:
            t = yf.Ticker(tick)
            th = threading.Thread(target=denormalize_and_append, daemon=True, args=(t, ticker_list, ))
            workers.append(th)
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join()
        workers = []
        logger.debug('batch {} out of {} complete, job is {}% complete'.format(i / batch_size + 1, len(tsx_tickers) / batch_size, (i / float(len(tsx_tickers)) * 100.0)))
        logger.debug('sleeping for 1 minute(s)...')
        time.sleep(60)
    full_set = pd.concat(ticker_list)
    con = sqlite3.connect('stocks.db')
    full_set.fillna('').astype(str).to_sql('tsx_info', con)
    con.close()
    return full_set


def generate_nasdaq_info():
    ticker_list = []
    workers = []
    batch_size = 10
    nasdaq_tickers = get_all_tickers()
    for i in range(0, len(nasdaq_tickers), batch_size):
        batch = nasdaq_tickers[i:i + batch_size]
        for tick in batch:
            t = yf.Ticker(tick)
            th = threading.Thread(target=denormalize_and_append, daemon=True, args=(t, ticker_list, ))
            workers.append(th)
        for worker in workers:
            worker.start()
        for worker in workers:
            worker.join()
        workers = []
        logger.debug('batch {} out of {} complete, job is {}% complete'.format(i / batch_size + 1, len(nasdaq_tickers) / batch_size, (i / float(len(nasdaq_tickers)) * 100.0)))
        logger.debug('sleeping for 30 second(s)...')
        time.sleep(30)
    full_set = pd.concat(ticker_list)
    con = sqlite3.connect('stocks.db')
    full_set.fillna('').astype(str).to_sql('nasdaq_info', con)
    con.close()
    return full_set


def calculate_volatility(ticker, timeframe='1y'):
    h = ticker.history(period=timeframe)
    h.sort_index(ascending=False, inplace=True)
    x = (np.log(h['Close'] / h['Close'].shift(-1)))
    x.dropna()
    std = np.std(x)
    s = std * TRADING_DAYS ** 0.5
    fig, ax = plt.subplots(1, 1, figsize=(7, 5))
    n, bins, patches = ax.hist(x.values, bins=50, alpha=0.65, color='blue')
    y = ((1 / (np.sqrt(2 * np.pi) * std)) *
         np.exp(-0.5 * (1 / std * (bins - x.mean())) ** 2))
    ax.plot(bins, y, '--', color="orange")
    ax.set_xlabel('log return of stock price')
    ax.set_ylabel('frequency of log return')
    ax.set_title('Historical Volatility for {}'.format(ticker.info['longName']))
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
    x = x_corr[0] + (x_corr[1] - x_corr[0]) / 15
    y -= (y_corr[1] - y_corr[0]) / 20
    fig.tight_layout()
    fig.savefig('historical_volatility.png')
    fig.show()


def plot_volatility(ticker):
    t = ticker.history(period='10y')
    returns = np.log(t['Close'] / t['Close'].shift(1))
    returns.fillna(0, inplace=True)
    volatility = returns.rolling(window=TRADING_DAYS).std() * np.sqrt(TRADING_DAYS)
    volatility.fillna(0, inplace=True)
    fig = plt.figure(figsize=(15, 7))
    ax1 = fig.add_subplot(1, 1, 1)
    volatility.plot(ax=ax1)
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Volatility')
    ax1.set_title('Annualized volatility for {}'.format(ticker.info['longName']))
    plt.show()


def compare_volatility(tickers_data):
    returns_portfolio = np.log(tickers_data['Close'] / tickers_data['Close'].shift(1))
    returns_portfolio.fillna(0, inplace=True)
    volatility_portfolio = returns_portfolio.rolling(window=TRADING_DAYS).std() * np.sqrt(TRADING_DAYS)
    volatility_portfolio.tail()
    fig = plt.figure(figsize=(15, 7))
    ax2 = fig.add_subplot(1, 1, 1)
    volatility_portfolio.plot(ax=ax2)
    ax2.set_xlabel('Date')
    ax2.set_ylabel('Volatility')
    ax2.set_title('Portfolio annualized volatility')
    plt.show()


def recreate_tsx_frame():
    con = sqlite3.connect('stocks.db')
    nf = pd.read_sql('select * from tsx_info', con)
    con.close()
    return nf


def recreate_nasdaq_frame():
    con = sqlite3.connect('stocks.db')
    nf = pd.read_sql('select * from nasdaq_info', con)
    con.close()
    return nf


def get_all_ticker_objects():
    tickers = []
    batch_size = 30
    tsx_tickers = ['{}.to'.format(t) for t in get_all_tsx_tickers()]
    for i in range(0, len(tsx_tickers), batch_size):
        batch = tsx_tickers[i:i + batch_size]
        ticks = yf.Tickers(' '.join(batch))
        tickers = tickers + ticks.tickers.values()
        logger.debug('batch {} complete.'.format(i))
    return tickers


def denormalize_and_append(ticker, list_of_dataframes):
    info_dict = ticker.info
    if not any(info_dict.values()):
        return
    row = dict((k, [v]) for k, v in info_dict.items())
    logger.debug('processed {}'.format(row['longName'][0]))
    list_of_dataframes.append(pd.DataFrame.from_dict(row, orient='columns'))


def main():
    try:
        con = sqlite3.connect('stocks.db')
        cur = con.cursor()
        cur.execute('''drop table tsx_info;''')
        cur.execute('''drop table nasdaq_info;''')
    except sqlite3.OperationalError as oe:
        logger.debug('Unable to drop db: {}'.format(oe))
    start_time = time.time()
    tsx_info = generate_tsx_info()
    nasdaq_info = generate_nasdaq_info()
    data_gathered = time.time()
    logger.info('TSX data gathered in {} seconds.'.format(data_gathered - start_time))
    return tsx_info, nasdaq_info


#some dataset gatherings
#pd.options.display.float_format = '${:,.2f}'.format
#nf.sort_values(by=['priceToBook'])[['shortName', 'symbol', 'shortRatio', 'profitMargins', 'priceToBook', 'sector', 'marketCap']].tail(30)
def numize(nf, column):
    nf[column] = pd.to_numeric(nf[column])
    nf[column] = nf[column].fillna(0.00)


#nf.to_string(formatters={'marketCap':'${:,.2f}'.format})
#nf.sort_values(by=['shortRatio'])[['shortName', 'symbol', 'shortRatio', 'profitMargins', 'priceToBook', 'sector', 'marketCap']].tail(30).plot.bar('shortName', 'shortRatio')

def dim_bar(nf, dimension, filter_dimension=None, filter=None, sort='tail', remove_zeros=False, money=False, depth=20):
    numize(nf, dimension)
    if money:
        pass
    if remove_zeros:
        nf = nf[(nf[dimension] != 0)]
    nf['name_and_ticker'] = nf[['longName', 'symbol']].agg(' '.join, axis=1)
    if filter:
        if not filter_dimension:
            nf = nf[nf[dimension] == filter]
        else:
            nf = nf[nf[filter_dimension] == filter]
    if sort == 'tail':
        axes_subplot = nf.sort_values(by=[dimension])[['name_and_ticker', dimension]].tail(depth).plot.barh('name_and_ticker', dimension, color=['green', 'lightgreen'], figsize=(12, 6))
        y = nf.sort_values(by=[dimension])[dimension].tail(depth).to_list()
    else:
        axes_subplot = nf.sort_values(by=[dimension])[['name_and_ticker', dimension]].head(depth).plot.barh('name_and_ticker', dimension, color=['green',  'lightgreen'], figsize=(12, 6))
        y = nf.sort_values(by=[dimension])[dimension].head(depth).to_list()
    for i, v in enumerate(y):
        axes_subplot.text(v + 0.1, i-0.2, '{:4.4f}'.format(v), color='orange')
    plt.tight_layout()
    plt.show()
    return axes_subplot

