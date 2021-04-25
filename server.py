import io
from gateways.ticker_gateway import TickerGateway
from gateways.market_gateway import MarketGateway
from server_helpers import buffer_fig
from flask import Flask, render_template
import jinja2

app = Flask(__name__)

templateLoader = jinja2.FileSystemLoader(searchpath="./templates")
templateEnv = jinja2.Environment(loader=templateLoader)


@app.route('/info/<ticker>')
def show_ticker_info(ticker):
    template = templateEnv.get_template('info_grid.tpl')
    ticker_info = TickerGateway().get_ticker_info(ticker)
    return template.render(ticker_info=ticker_info)


@app.route('/d3/top/nasdaq/<dimension>')
def nasdaq_dimension(dimension):
    data = MarketGateway().json_dimension(dimension)
    return data


@app.route('/d3/top/nasdaq/<dimension>/sector/<sector>')
def nasdaq_dimension_by_sector(dimension):
    data = MarketGateway().json_dimension_by_sector(dimension, sector)
    return data


@app.route('/d3/top/nasdaq/<dimension>/industry/<industry>')
def nasdaq_dimension_by_industry(dimension, industry):
    data = MarketGateway().json_dimension(dimension, industry)
    return data


@app.route('/d3/chart/nasdaq/<dimension>')
def show_nasdaq_bar_beta(dimension):
    template = templateEnv.get_template('d3_dim_bar.tpl')
    return template.render(dimension=dimension)


@app.route('/d3/chart/nasdaq/<dimension>/sector/<sector>')
def show_nasdaq_bar_beta_by_sector(dimension, sector):
    template = templateEnv.get_template('d3_dim_bar.tpl')
    return template.render(dimension=dimension, sector=sector)


@app.route('/d3/chart/nasdaq/<dimension>/industry/<industry>')
def nshow_nasdaq_bar_beta_by_industry(dimension, industry):
    template = templateEnv.get_template('d3_dim_bar.tpl')
    return template.render(dimension=dimension, industry=industry)


@app.route('/volatility/<ticker>')
def calculate_volatility(ticker):
    fig = TickerGateway().calculate_volatility(ticker)
    return buffer_fig(fig)


@app.route('/volatility/long/<ticker>')
def plot_volatility(ticker):
    fig = TickerGateway().plot_volatility(ticker)
    return buffer_fig(fig)


@app.route('/top/tsx/<dimension>')
def show_tsx_bar(dimension):
    fig = MarketGateway().top_tsx(dimension)
    return buffer_fig(fig)


@app.route('/top/nasdaq/<dimension>')
def show_nasdaq_bar(dimension):
    fig = MarketGateway().top_nasdaq(dimension)
    return buffer_fig(fig)


@app.route('/top/tsx/<sector>/<dimension>')
def show_tsx_bar_by_sector(sector, dimension):
    fig = MarketGateway().top_tsx(dimension, sector=sector)
    return buffer_fig(fig)


@app.route('/top/nasdaq/<sector>/<dimension>')
def show_nasdaq_bar_by_sector(sector, dimension):
    fig = MarketGateway().top_nasdaq(dimension, sector=sector)
    return buffer_fig(fig)


if __name__ == "__main__":
    app.run(debug=True)

