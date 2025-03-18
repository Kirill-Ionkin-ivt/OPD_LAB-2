from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
import requests
import warnings

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)


def parse_usd_rate():
    url = 'https://www.cbr.ru/scripts/XML_daily.asp'
    page = requests.get(url)

    soup = BeautifulSoup(page.content, "html.parser")

    currencies = soup.find_all('valute')

    # Проходим по всем валютам и ищем доллар США
    for currency in currencies:
        if currency.find('charcode').text == 'USD':
            rate = currency.find('value').text
            print(f"Курс доллара: {rate} руб.")
            return rate


# Вызов функции
usd_rate = parse_usd_rate()