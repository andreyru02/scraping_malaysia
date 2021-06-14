import requests
from bs4 import BeautifulSoup as bs
import time
import csv
import re

# TODO: Бандар Мири
# TODO: Бандар-Лабуан

URL = 'http://2pos.guru'
CITY = []
pattern = r'(.*)(2F%2F)(www.[A-z]*.[A-z]*.?[A-z]+)(%2F)(.*)?'
sub = r'\3'

with open('city.txt', 'r') as f:
    for city in f.readlines():
        CITY.append(city.strip('\n'))


def get_city_url():
    """ Получаем URL городов """
    city_urls = []
    with requests.Session() as s:
        resp = s.get(URL)
        soup = bs(resp.text, 'html.parser')

    for el in soup.select('.cities_box'):
        for name in el.find_all('a'):
            if name.text in CITY:
                city_urls.append(URL + name.get('href'))

    return city_urls


def scrap_cats_box():
    """  """
    city_urls = get_city_url()
    with requests.Session() as s:
        for url in city_urls:
            resp = s.get(url)  # Открываем страницу города
            time.sleep(0.33)
            soup = bs(resp.text, 'html.parser')

            for box in soup.select('.cats_box'):
                for names in box.find_all('a'):
                    name_catalog = names.text  # Название каталога
                    name_url = names.get('href')  # URL бокса

                    get_url_firms(name_catalog, name_url)


def get_url_firms(name, url):
    """ Парсим ссылки на организации """
    firms_url = []
    with requests.Session() as s:
        resp = s.get(URL + url)
        soup = bs(resp.text, 'html.parser')
        try:
            count_pages = soup.find('div', class_='page_count lcalign').text[-1]
        except AttributeError:
            count_pages = 1

        for num in range(int(count_pages)):
            resp = s.get(f'{URL+ url}/{num + 1}')
            time.sleep(0.33)
            soup = bs(resp.text, 'html.parser')
            for firms in soup.select('.catalog_left'):
                for firm in firms.find_all('div', class_='item_name'):
                    firms_url.append(URL + firm.find('a').get('href'))

    scrap_firm(name, firms_url)


def scrap_firm(name_box, firms_url):
    """Парсим организацию"""
    with requests.Session() as s:
        for firm_url in firms_url:
            print(firm_url)
            resp = s.get(firm_url)
            time.sleep(0.33)
            soup = bs(resp.text, 'html.parser')

            for el in soup.select('.firm_left'):
                data = []
                try:
                    title = el.find('div', class_='firm_title').text.split(',')
                    name = title[0]
                    city = title[1]
                except AttributeError:
                    name = ''
                    city = ''
                try:
                    address = el.find('div', class_='firm_address').text
                except AttributeError:
                    address = ''
                try:
                    phone = el.find('div', class_='firm_phone').find('a').text
                except AttributeError:
                    phone = ''
                try:
                    website_ = el.find('div', class_='firm_website').find('a').get('href')
                    website = re.sub(pattern, sub, website_)
                except AttributeError:
                    website = ''

                data.append(name)
                data.append(address)
                data.append(website)
                data.append(phone)
                data.append(name_box)
                data.append(city)

                print(data)

                write_csv(data)


def write_csv(data):
    """Записываем в csv"""
    data_write = [data]
    with open("data.csv", "a", newline="") as f:
        datawriter = csv.writer(f, delimiter=',')
        datawriter.writerows(data_write)


if __name__ == '__main__':
    scrap_cats_box()
