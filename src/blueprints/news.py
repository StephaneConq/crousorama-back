from flask import Blueprint, jsonify
import requests
from bs4 import BeautifulSoup

news_blueprint = Blueprint('news', __name__)


@news_blueprint.route('')
def get_news():
    news = []
    r = requests.get('https://www.lemonde.fr/bourse/')
    html = r.text
    soup = BeautifulSoup(html)
    news_html = soup.findAll("section", {"class": "teaser--inline-picture"})
    for n_html in news_html:
        tmp_news = {}
        img_soup = BeautifulSoup(str(n_html)).findAll("img")
        tmp_news["img"] = img_soup[1].attrs["src"]
        news_soup = BeautifulSoup(str(n_html)).find("a", {"class": "teaser__link"})
        tmp_news["url"] = news_soup.attrs["href"]
        tmp_news["title"] = BeautifulSoup(str(news_soup)).find("h3", {"class": "teaser__title"}).text
        tmp_news["summary"] = BeautifulSoup(str(news_soup)).find("p", {"class": "teaser__desc"}).text
        meta_soup = BeautifulSoup(str(n_html)).find("p", {"class": "meta__publisher"})
        tmp_news["publication_date"] = BeautifulSoup(str(meta_soup)).find('span', {"class": "meta__date"}).text
        try:
            tmp_news["author"] = BeautifulSoup(str(meta_soup)).find('a', {"class": "article__author-link"}).text
        except AttributeError:
            tmp_news["author"] = BeautifulSoup(str(meta_soup)).find('span', {"class": "meta__author"}).text
            print()
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
