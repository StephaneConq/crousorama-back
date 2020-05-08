from bs4 import BeautifulSoup
from flask import Blueprint, request, jsonify
import requests

finance_blueprint = Blueprint('finance', __name__)


@finance_blueprint.route('/search')
def search():
    q = request.args.get('q')
    req = requests.get('https://www.tradingsat.com/async/json/instrument-search.php?term={}'.format(q))
    return jsonify(req.json()), 200


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
    return remove_jumps(string).replace(' ', '') if '\n' in string else string


def remove_jumps(string):
    return string.replace('\n', '')


@finance_blueprint.route('/stock/<stock_id>/<tab>')
def get_tab_data(stock_id, tab):
    if tab == 'cours':
        return jsonify(get_cours(stock_id))
    elif tab == 'graphique':
        return jsonify(get_graphique(stock_id))
    elif tab == 'actualites':
        return jsonify(get_actualites(stock_id, request.args.get('page')))
    elif tab == 'conseils':
        return jsonify(get_conseils(stock_id, request.args.get('page')))
    elif tab == 'agenda':
        return jsonify(get_calendar(stock_id))
    elif tab == 'dividendes':
        return jsonify(get_dividends(stock_id))
    elif tab == 'societe':
        return jsonify(get_company(stock_id))


def get_cours(stock_id):
    res = requests.get('https://www.tradingsat.com/{}'.format(stock_id))
    html = res.text
    html_soup = BeautifulSoup(html)
    tmp = {
        'id': html_soup.find('span', {'class': 'mnemo'}).text.split(' - ')[0] + '.PA',
        'name': html_soup.find('h1').text,
        'price': html_soup.find('span', {'class': 'price'}).text,
        'variation': html_soup.find('span', {'class': 'variation'}).text,
    }
    for item_row in html_soup.findAll('div', {'class': 'item-row'}):
        text_splitted = item_row.text.split(' :')
        key = remove_jumps(text_splitted[0])
        try:
            value = remove_jumps(text_splitted[1])
        except Exception:
            value = '-'
        tmp[key] = value
    return tmp


def get_graphique(stock_id):
    res = requests.get('https://www.tradingsat.com/{}/graphique.html'.format(stock_id))
    html = res.text
    html_soup = BeautifulSoup(html)
    iframe = html_soup.find('iframe')
    return {'url': iframe.attrs['src']}


def get_actualites(stock_id, page=1):
    res = requests.get('https://www.tradingsat.com/{}/actualites-{}.html'.format(stock_id, page))
    html = res.text
    html_soup = BeautifulSoup(html)
    news = []
    for item in html_soup.findAll('div', {'class': 'item'}):
        item_soup = BeautifulSoup(str(item))
        try:
            tmp = {
                'date': remove_jumps(item_soup.find('div', {'class': 'item-date'}).text).replace(' ', ''),
                'title': item_soup.find('a').text,
                'link': 'https://www.tradingsat.com' + item_soup.find('a').attrs['href'],
            }
            news.append(tmp)
        except AttributeError:
            continue
    return news


def get_conseils(stock_id, page):
    res = requests.get('https://www.tradingsat.com/{}/conseils-{}.html'.format(stock_id, page))
    html = res.text
    html_soup = BeautifulSoup(html)
    conseils = []
    for item in html_soup.findAll('div', {'class': 'item'}):
        item_soup = BeautifulSoup(str(item))
        try:
            tmp = {
                'date': remove_jumps(item_soup.find('div', {'class': 'item-date'}).text).replace(' ', ''),
                'title': remove_jumps(item_soup.find('a').text),
                'link': 'https://www.tradingsat.com' + item_soup.find('a').attrs['href'],
            }
            variation = item_soup.find('span', {'class': 'variation'})
            tmp['class'] = 'red' if 'var-down' in variation.attrs['class'] else 'green'
            conseils.append(tmp)
        except AttributeError:
            continue
    return conseils


def get_calendar(stock_id):
    res = requests.get('https://www.tradingsat.com/{}/agenda.html'.format(stock_id))
    html = res.text
    html_soup = BeautifulSoup(html)
    blocs = html_soup.findAll('div', {'class': 'sub-col'})
    events = {
        'upcoming': [],
        'past': []
    }
    for item in BeautifulSoup(str(blocs[0])).findAll('div', {'class': 'item'}):
        events['upcoming'].append(create_event(BeautifulSoup(str(item))))
    for item in BeautifulSoup(str(blocs[1])).findAll('div', {'class': 'item'}):
        events['past'].append(create_event(BeautifulSoup(str(item))))
    return events


def create_event(item):
    item_soup = BeautifulSoup(str(item))
    return {
        'date': remove_jumps(item_soup.find('div', {'class': 'item-date'}).text).replace(' ', ''),
        'title': remove_jumps(item_soup.find('div', {'class': 'item-text'}).text),
    }


def get_dividends(stock_id):
    res = requests.get('https://www.tradingsat.com/{}/dividende.html'.format(stock_id))
    html = res.text
    html_soup = BeautifulSoup(html)
    dividends = []
    tables = html_soup.findAll('table')
    for idx, row in enumerate(BeautifulSoup(str(tables[0])).findAll('tr')):
        if idx == 0:
            continue
        try:
            dividends.append({
                'year': row.contents[1].text,
                'detachment': row.contents[3].text,
                'payment': row.contents[5].text,
                'type': row.contents[7].text,
                'amount': row.contents[9].text,
            })
        except IndexError as e:
            continue
    return dividends


def get_company(stock_id):
    res = requests.get('https://www.tradingsat.com/{}/societe.html'.format(stock_id))
    html = res.text
    html_soup = BeautifulSoup(html)
    paragraphs = html_soup.findAll('p')
    return {'description': paragraphs[0].text}
