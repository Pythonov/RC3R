import requests
from bs4 import BeautifulSoup

URL = "http://zakupki.rosatom.ru/2109025610642"
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
}


def get_html(url, params=None):
    r = requests.get(url, headers=HEADERS, params=params)
    return r


def parse_page(url):
    html = get_html(url)
    if html.status_code == 200:
        text = html.text
        return text
    else:
        print("wtf")
