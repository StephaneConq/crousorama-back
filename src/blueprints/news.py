from flask import Blueprint, jsonify
import requests
from bs4 import BeautifulSoup

news_blueprint = Blueprint('news', __name__)


@news_blueprint.route('')
def get_news():
    news = []
    r = requests.get('https://www.lesechos.fr/bourse')
    html = r.text
    soup = BeautifulSoup(html)
    news_html = soup.findAll("a", {"class": "dfBjtz"})
    for n_html in news_html:
        tmp_news = {
            'url': n_html.attrs['href']
        }
        first_child = n_html.contents[0]
        tmp_news['title'] = first_child.contents[1].next
        link_soup = BeautifulSoup(str(n_html))
        dates = link_soup.findAll("span", {"class": "gfNWwB"})
        tmp_news['publication_date'] = dates[0].next
        summary = link_soup.findAll("div", {"class": "ewoSIL"})
        tmp_news['summary'] = summary[0].next
        news.append(tmp_news)
    return jsonify(news), 200


def find_publish_date(contents):
    for content in contents:
        if type(content) == 'str':
            return content.next
        if content.contents is None:
            pass
        return find_publish_date(content.contents)


@news_blueprint.route('/realtime')
def get_realtime_news():
    r = requests.get('https://investir.lesechos.fr/index.php')
    soup = BeautifulSoup(r.text)
    realtime_container = soup.find("div", {"class": "contenu-dernieres-infos"})
    news_links = realtime_container.findAllNext("a")
    news = []
    for n in news_links:
        try:
            tmp_n = {
                'date': n.contents[1].attrs['datetime'],
                'title': clean(n.contents[5].text)
            }
            news.append(tmp_n)
        except IndexError:
            continue
        except KeyError:
            continue
    return jsonify(news), 200


def clean(string):
    tmp = string.replace('\t', '').replace('\r', '').replace('\n', '').split('                             ')[0]
    if len(tmp.split('Conseil Investir')) > 1:
        tmp = tmp.split('Conseil Investir')[1]
    if len(tmp.split('Les recos des analystes :')) > 1:
        tmp = tmp.split('Les recos des analystes :')[1]
    return tmp
