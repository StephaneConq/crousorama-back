from flask import Blueprint, jsonify
import requests
from bs4 import BeautifulSoup

calendar_blueprint = Blueprint('agenda', __name__)


@calendar_blueprint.route('')
def get_agenda():
    req = requests.get('https://www.boursier.com/agenda-boursier/')
    html = req.text
    soup = BeautifulSoup(html)
    agenda = soup.find('div', {'id': 'agenda-bourse'})
    titles = BeautifulSoup(str(agenda)).findAll('h2')
    tables = BeautifulSoup(str(agenda)).findAll('table')
    agenda_dict = {}
    title_headers = []
    for t in titles:
        title_headers.append(str(t.string))
    for idx, t in enumerate(tables):
        tmp = {}
        rows = BeautifulSoup(str(t)).findAll('tr')
        current_row = ''
        current_country = ''
        for r in rows:
            if len(r.contents) == 1:
                current_row = str(r.contents[0].string)
                if current_row.startswith('Sociétés'):
                    tmp[current_row] = []
                else:
                    tmp[current_row] = {}
            if len(r.contents) == 6:
                if current_row.startswith('Société'):
                    tmp[current_row].append({
                        'name': str(r.contents[0].text),
                        'event': str(clean(r.contents[2].text))
                    })
                else:
                    current_country = str(r.contents[0].string)
                    if current_country not in tmp[current_row]:
                        tmp[current_row][current_country] = []
                    tmp[current_row][current_country].append(clean(r.contents[2].next))
            if len(r.contents) == 7:
                if current_row.startswith('Sociétés'):
                    tmp[current_row].append({
                        'name': str(r.contents[1].string),
                        'event': str(clean(r.contents[3].text))
                    })
                else:
                    clean_value = clean_with_strong_html(r.contents[3])
                    tmp[current_row][current_country].append(clean_value)
        agenda_dict[title_headers[idx]] = tmp
    return jsonify(agenda_dict), 200


def clean(string):
    return string.replace('\t', '').replace('\r', '').replace('\n', '')


def clean_with_strong_html(tag_array):
    return tag_array.contents[0] + ' : ' + clean(tag_array.contents[3].string)
