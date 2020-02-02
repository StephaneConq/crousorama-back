from flask import Blueprint, request, jsonify
import requests
import yfinance as yf
import pandas as pd
from src.config import CONFIG
import json

finance = Blueprint('finance', __name__)


@finance.route('/search')
def query():
    search = request.args.get('q')
    req = requests.get('https://query1.finance.yahoo.com/v1/finance/search?q={}&quotesCount=6&enableFuzzyQuery=false'
                       .format(search))
    return jsonify(req.json().get('quotes', [])), 200


@finance.route('/indice/<symbol>')
def get_by_symbol(symbol):
    range_arg = request.args.get('range')
    req = requests.get('https://query1.finance.yahoo.com/v8/finance/chart/{}?region=FR&lang=FR&includePrePost=false&interval=1d&range={}'
                       .format(symbol, range_arg if range_arg else '1d'))
    return jsonify(req.json().get('chart', {}).get('result', [{}])[0]), 200


@finance.route('/indice/<symbol>/history')
def get_history(symbol):
    time = request.args.get('period')
    stock = yf.Ticker(symbol)
    history = stock.history(period=time)
    df = pd.DataFrame(history,
                      columns=CONFIG.get('history'))
    history_json = df.to_json(orient='records')
    try:
        history_json = json.loads(history_json)
    except Exception as e:
        history_json = []
    return jsonify({"history": history_json}), 200
