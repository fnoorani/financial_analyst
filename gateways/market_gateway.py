import sqlite3
import json
import pandas as pd
import matplotlib.pyplot as plt

def recreate_tsx_frame():
    con = sqlite3.connect('spikes/stocks.db')
    nf = pd.read_sql('select * from tsx_info', con)
    con.close()
    return nf


def recreate_nasdaq_frame():
    con = sqlite3.connect('spikes/stocks.db')
    nf = pd.read_sql('select * from nasdaq_info', con)
    con.close()
    return nf


def numize(nf, column):
    nf[column] = pd.to_numeric(nf[column])
    nf[column] = nf[column].fillna(0.00)


def dim_bar(nf, dimension, filter_dimension=None, filter=None, sort='tail', remove_zeros=False, depth=20):
    fig, ax = plt.subplots(1, 1, figsize=(13, 13))
    numize(nf, dimension)
    if remove_zeros:
        nf = nf[(nf[dimension] != 0)]
    nf['name_and_ticker'] = nf[['longName', 'symbol']].agg(' '.join, axis=1)
    if filter:
        if not filter_dimension:
            nf = nf[nf[dimension] == filter]
        else:
            nf = nf[nf[filter_dimension] == filter]
    if sort == 'tail':
        ax.barh(nf.sort_values(by=[dimension])['name_and_ticker'].tail(depth).values,
                nf.sort_values(by=[dimension])[dimension].tail(depth).values, color=['blue', 'darkblue'])
        y = nf.sort_values(by=[dimension])[dimension].tail(depth).to_list()
    else:
        ax.barh(nf.sort_values(by=[dimension])['name_and_ticker'].head(depth).values,
                nf.sort_values(by=[dimension])[dimension].head(depth).values, color=['blue', 'darkblue'])
        y = nf.sort_values(by=[dimension])[dimension].head(depth).to_list()
    for i, v in enumerate(y):
        suffix = ''
        q = v
        if v > 10 ** 6:
            q = v / 10 ** 6
            suffix = 'M'
        if v > 10 ** 9:
            q = v / 10 ** 9
            suffix = 'B'
        if v > 10 ** 12:
            q = v / 10 ** 12
            suffix = 'T'
        ax.text(v, i-0.2, '{:4.2f} {}'.format(q, suffix), color='yellow', ha='right', fontweight='bold', fontsize=7)
    fig.tight_layout()
    return fig


class MarketGateway(object):
    @staticmethod
    def top_tsx(dimension, sector='all'):
        tsx = recreate_tsx_frame()
        if sector == 'all':
            return dim_bar(tsx, dimension, depth=55)
        else:
            return dim_bar(tsx, dimension, depth=55, filter_dimension='sector', filter=sector)

    @staticmethod
    def top_nasdaq(dimension, sector='all'):
        nas = recreate_nasdaq_frame()
        if sector == 'all':
            return dim_bar(nas, dimension, depth=55)
        else:
            return dim_bar(nas, dimension, depth=55, filter_dimension='sector', filter=sector)

    @staticmethod
    def json_dimension(dimension):
        nas = recreate_nasdaq_frame()
        numize(nas, dimension)
        nas['name_and_ticker'] = nas[['longName', 'symbol']].agg(' '.join, axis=1)
        d = nas.sort_values(by=[dimension])[['name_and_ticker', dimension]].dropna().tail(50).to_dict()
        ix = []
        for indx, value in d['name_and_ticker'].items():
            ix.append({"label": value, "n": d[dimension][indx]})
        ix.reverse()
        ret = {"items": ix}
        return json.dumps(ret)

    @staticmethod
    def json_dimension_by_sector(dimension, sector):
        nas = recreate_nasdaq_frame()
        numize(nas, dimension)
        nas['name_and_ticker'] = nas[nas['sector'] == sector][['longName', 'symbol']].agg(' '.join, axis=1)
        d = nas.sort_values(by=[dimension])[['name_and_ticker', dimension]].dropna().tail(50).to_dict()
        ix = []
        for indx, value in d['name_and_ticker'].items():
            ix.append({"label": value, "n": d[dimension][indx]})
        ix.reverse()
        ret = {"items": ix}
        return json.dumps(ret)

    @staticmethod
    def json_dimension_by_industry(dimension, industry):
        nas = recreate_nasdaq_frame()
        numize(nas, dimension)
        nas['name_and_ticker'] = nas[nas['industry'] == industry][['longName', 'symbol']].agg(' '.join, axis=1)
        d = nas.sort_values(by=[dimension])[['name_and_ticker', dimension]].dropna().tail(50).to_dict()
        ix = []
        for indx, value in d['name_and_ticker'].items():
            ix.append({"label": value, "n": d[dimension][indx]})
        ix.reverse()
        ret = {"items": ix}
        return json.dumps(ret)

