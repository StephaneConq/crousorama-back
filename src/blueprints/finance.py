from bs4 import BeautifulSoup
from flask import Blueprint, request, jsonify
import requests

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
    req = requests.get(
        'https://query1.finance.yahoo.com/v8/finance/chart/{}?region=FR&lang=FR&includePrePost=false&interval=1d&range={}'
        .format(symbol, range_arg if range_arg else '1d'))
    results = {}
    results["indicators"] = req.json().get('chart', {}).get('result', [{}])[0].get("indicators")
    results["meta"] = req.json().get('chart', {}).get('result', [{}])[0].get("meta")
    results["timestamp"] = req.json().get('chart', {}).get('result', [{}])[0].get("timestamp")
    req = requests.get(
        'https://query2.finance.yahoo.com/v10/finance/quoteSummary/{}?lang=fr-FR&region=FR&modules=earnings%2CesgScores%2Cdetails&corsDomain=finance.yahoo.com'
            .format(symbol))
    results["earningsChart"] = req.json().get('quoteSummary', {}).get('result', [{}])[0].get("earnings", {}).get(
        "earningsChart")
    results["financialsChart"] = req.json().get('quoteSummary', {}).get('result', [{}])[0].get("earnings", {}).get(
        "financialsChart")
    return jsonify(results), 200


@finance_blueprint.route('/palmares')
def get_palmares():
    req = requests.get('https://m.investir.lesechos.fr/marches/palmares/palmares.php')
    html = req.text
    soup = BeautifulSoup(html)
    blocs = soup.findAll('div', {'class': ['row', 'indice']})
    rows = []
    for b in blocs:
        row_soup = BeautifulSoup(str(b))
        tmp = {
            'indice': row_soup.find('div', {'class': 'nom-indice'}).text,
            'meta': row_soup.find('span', {'class': 'place-heure'}).text,
            'value': row_soup.find('span', {'class': 'val-indice'}).text,
            'variation': row_soup.find('span', {'class': 'var-indice'}).text,
        }
        if not palmares_already_pushed(tmp['indice'], rows):
            rows.append(tmp)
    return jsonify(rows)


def palmares_already_pushed(quote, list):
    matches = [x for x in list if x['indice'] == quote]
    return len(matches) > 0


@finance_blueprint.route('/palmares_dividend')
def get_palmares_dividend():
    page = request.args.get('page')
    req = requests.get('https://www.boursorama.com/bourse/actions/palmares/dividendes/page-{}'
                       .format(page if page is not None else '1'))
    html = req.text
    soup = BeautifulSoup(html)
    rows = soup.findAll('tr', {'class': 'c-table__row'})
    headers = []
    dividends = []
    for idx, row in enumerate(rows):
        tmp = {}
        for idx_cell, cell in enumerate(row.contents):
            if idx == 0:
                headers.append(cell.text)
            else:
                try:
                    tmp[headers[idx_cell]] = parse_spaces(cell.text)
                except AttributeError as e:
                    continue
        if tmp != {}:
            dividends.append(tmp)
    return jsonify(dividends)


def parse_spaces(string):
    return string.replace('\n', '').replace(' ', '') if '\n' in string else string