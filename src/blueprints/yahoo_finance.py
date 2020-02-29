from flask import Blueprint, request, jsonify
import requests
import yfinance as yf
import pandas as pd
from src.config import CONFIG
import json


finance_blueprint = Blueprint('finance', __name__)


@finance_blueprint.route('/search')
def query():
    search = request.args.get('q')
    req = requests.get('https://query1.finance.yahoo.com/v1/finance/search?q={}&quotesCount=10&enableFuzzyQuery=false'
                       .format(search))
    return jsonify(req.json().get('quotes', [])), 200


@finance_blueprint.route('/indice/<symbol>')
def get_by_symbol(symbol):
    range_arg = request.args.get('range')
    req = requests.get('https://query1.finance.yahoo.com/v8/finance/chart/{}?region=FR&lang=FR&includePrePost=false&interval=1d&range={}'
                       .format(symbol, range_arg if range_arg else '1d'))
    results = {}
    results["indicators"] = req.json().get('chart', {}).get('result', [{}])[0].get("indicators")
    results["meta"] = req.json().get('chart', {}).get('result', [{}])[0].get("meta")
    results["timestamp"] = req.json().get('chart', {}).get('result', [{}])[0].get("timestamp")
    req = requests.get(
        'https://query2.finance.yahoo.com/v10/finance/quoteSummary/{}?lang=fr-FR&region=FR&modules=earnings%2CesgScores%2Cdetails&corsDomain=finance.yahoo.com'
        .format(symbol))
    results["earningsChart"] = req.json().get('quoteSummary', {}).get('result', [{}])[0].get("earnings", {}).get("earningsChart")
    results["financialsChart"] = req.json().get('quoteSummary', {}).get('result', [{}])[0].get("earnings", {}).get("financialsChart")
    return jsonify(results), 200


@finance_blueprint.route('/indice/<symbol>/history')
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