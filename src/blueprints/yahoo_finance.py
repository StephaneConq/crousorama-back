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
    req = requests.get('https://fr.finance.yahoo.com/_finance_doubledown/api/resource/content;fetchNewAttribution=true;getDetailView=true;getFullLcp=false;imageResizer=null;relatedContent=%7B%22enabled%22%3Atrue%7D;site=finance;ssEP=;useSlingstoneLcp=true;uuids=%5B%22f7967a86-8594-3bcb-b460-ca2c31333096%22%2C%22fb7151b7-929f-38f4-bd98-ec39e781778a%22%2C%220bd4e665-7d52-3533-947e-bdc6fb1eb919%22%2C%220f5b6945-9a5e-39a9-8024-600a6f4a70d9%22%2C%228a6bb89c-02e4-38fe-8bfc-9c795027e628%22%2C%229dc4bcb5-8f9d-3b0c-98c4-bcfbec4b1715%22%2C%22906020e7-bc29-39ac-95e8-817ed75c9db8%22%2C%22f29dc5e8-8b84-3181-a4f5-71379013f366%22%2C%22bc63c31c-f013-3ec8-9486-28e0d0b2ba59%22%2C%22062f3c6e-bcaa-3d51-828f-32fe2a13a590%22%2C%22903aa9e3-3669-326a-9607-2a604b3ef6ef%22%2C%22245fe9da-1e93-3481-b26e-bb42f42b1ced%22%2C%222d9d53ff-e407-35fb-944c-6469b63e735b%22%2C%22e918467c-ca8d-3924-b672-a0d508b307d7%22%2C%2258006a11-7b77-309d-b624-519893c5b67d%22%2C%222d6424ba-b7d1-3b90-9574-ec13dafeadf0%22%5D?bkt=fdstr-fr-ncp&device=desktop&feature=canvassOffnet%2CccOnMute%2Cdebouncesearch100%2CdeferDarla%2CecmaModern%2CemptyServiceWorker%2CenableCMP%2CenableConsentData%2CenableTheming%2CenableNavFeatureCue%2CenableGuceJs%2CenableGuceJsOverlay%2CenablePrivacyUpdate%2CenableVideoURL%2CnewContentAttribution%2CnewLogo%2CrelatedVideoFeatureOff%2CvideoNativePlaylist%2CenablePremiumFinancials%2CenableCCPAFooter%2CenhanceAddToWL%2CenableStageAds%2CsponsoredAds&intl=fr&lang=fr-FR&partner=none&prid=djf61dlf4acj9&region=FR&site=finance&tz=Europe%2FParis&ver=0.102.3258&returnMeta=true')
    return jsonify(req.json().get('data', {}).get('items', [])), 200
