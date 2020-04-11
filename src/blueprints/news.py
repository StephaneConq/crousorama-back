from flask import Blueprint, jsonify, request
import requests
from bs4 import BeautifulSoup

from src.config import CONFIG

news_blueprint = Blueprint('news', __name__)


@news_blueprint.route('')
def get_news():
    """
    get news
    :return: dict {
        img: str,
        url: str,
        title: str,
        summary: str,
        publication_date: str
    }
    """
    news = []
    page = request.args.get('page') or 1
    r = requests.get('https://www.reuters.com/news/archive/businessnews?view=page&page={}&pageSize=10'.format(page))
    html = r.text
    soup = BeautifulSoup(html)
    news_html = soup.findAll("article", {"class": "story"})
    for n_html in news_html:
        article_soup = BeautifulSoup(str(n_html))
        tmp_news = {
            "img": clean_url(article_soup.findAll("img")[0].attrs["org-src"])
            if "org-src" in article_soup.findAll("img")[0].attrs else CONFIG["news_img"],
            "url": "https://www.reuters.com" + article_soup.findAll("a")[0].attrs["href"],
            "title": clean(article_soup.findAll("h3")[0].text),
            "summary": article_soup.findAll("p")[0].text if len(article_soup.findAll("p")) > 0 else "",
            "publication_date": clean(article_soup.findAll("time")[0].text)
            if len(article_soup.findAll("time")) > 0 else ""
        }
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


def clean_url(string: str):
    return string.replace("amp;", "")
