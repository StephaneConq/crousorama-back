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
    req = requests.get('https://query1.finance.yahoo.com/v1/finance/search?q={}&quotesCount=10&enableFuzzyQuery=false'
                       .format(search))
    return jsonify(req.json().get('quotes', [])), 200


@finance.route('/indice/<symbol>')
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


@finance.route('/news')
def get_news():
    req = requests.get('https://fr.finance.yahoo.com/_finance_doubledown/api/resource/content;fetchNewAttribution=true;getDetailView=true;getFullLcp=false;imageResizer=null;relatedContent=%7B%22enabled%22%3Atrue%7D;site=finance;ssEP=;useSlingstoneLcp=true;uuids=%5B%22daeb8e0d-26d6-3611-bd51-382912bddd07%22%2C%22234d21c9-7f58-3c36-8f81-2bf59539dd90%22%2C%224669f3f7-f0e3-3841-b549-8d499cb69756%22%2C%22871bb69b-f2d0-3053-8d32-011e40577a7e%22%2C%227521e6b6-5141-3a81-8f6b-39e124066e2a%22%2C%222afbae28-2752-354b-9cc1-9a465ac13510%22%2C%22c2cf4727-d5ad-37d3-9be5-3dd9dbdbd182%22%2C%2210db7bf0-60a7-3b3a-8c53-688e1fae58b1%22%2C%225efe1aeb-1ed5-36a2-8828-20373e1d5f9d%22%2C%2277b308fd-41bd-3eeb-a82b-9a777dc07101%22%2C%22fc1c5121-1bff-3036-b8a7-3c68aa5a1528%22%2C%22ab789419-53a5-3415-9d34-69dda62e4e7b%22%2C%2245e81ca6-64a9-3a2a-99e2-95921f16171d%22%2C%22734d8afb-5c0c-34cd-99e2-6aea3215d5ff%22%2C%22c60f8416-5909-30c3-a360-8626143d320b%22%2C%224d6d7920-a5ec-3ab1-93ca-558d36343f43%22%5D?bkt=finance-FR-fr-FR-def&feature=canvassOffnet%2CccOnMute%2Cdebouncesearch100%2CdeferDarla%2CecmaModern%2CemptyServiceWorker%2CenableCMP%2CenableConsentData%2CenableTheming%2CenableNavFeatureCue%2CenableGuceJs%2CenableGuceJsOverlay%2CenablePrivacyUpdate%2CenableVideoURL%2CnewContentAttribution%2CnewLogo%2CrelatedVideoFeatureOff%2CvideoNativePlaylist%2CenablePremiumFinancials%2CenableCCPAFooter%2CenhanceAddToWL%2CenableStageAds%2CsponsoredAds&intl=fr&lang=fr-FR&prid=2dp0jf9f468h9&region=FR&site=finance&tz=Europe%2FParis&returnMeta=true')
    return jsonify(req.json().get('data', {}).get('items', [])), 200
