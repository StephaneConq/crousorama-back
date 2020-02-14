from flask import Blueprint, request, jsonify
import requests
from bs4 import BeautifulSoup

lesechos_news = Blueprint('lesechos_news', __name__)


@lesechos_news.route('')
def get_news():
    news = []
    r = requests.get('https://www.lesechos.fr/bourse')
    html = r.text
    soup = BeautifulSoup(html)
    news_html = soup.findAll("a", {"class": "XMwLM"})
    for n_html in news_html:
        tmp_news = {
            'url': n_html.attrs['href']
        }
        first_child = n_html.contents[0]
        tmp_news['title'] = first_child.contents[1].next
        link_soup = BeautifulSoup(str(n_html))
        dates = link_soup.findAll("span", {"class": "caIHMU"})
        tmp_news['publication_date'] = dates[0].next
        summary = link_soup.findAll("div", {"class": "bAHvz"})
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
