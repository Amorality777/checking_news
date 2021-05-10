import datetime

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from requests.exceptions import InvalidSchema, InvalidURL

from logs.settings import setup_logger
from news_parser.models import Topic, News, BrokenLink

log = setup_logger()


class NewsParser:
    url = 'https://kodeks.ru/news'

    @classmethod
    def run(cls) -> None:
        """Добавляет все новости за полседний день в бд
        Есть возможность расширить функционал с выбором даты"""
        soup = cls._get_soup()
        news_block = cls._get_news_block(soup)
        news_blocks = news_block.find_all('div', attrs={'class': ['news_i ', 'news_tile']}, recursive=False)
        for topic_data in news_blocks:
            topic_name = cls._get_topic_name(topic_data)
            topic = cls._get_topic(topic_name)
            news_list = cls._get_news_list(topic_data)
            for news in news_list:
                title = news.text.strip()
                link = news["href"]
                cls._add_news(topic, title, link)

    @staticmethod
    def _add_news(topic: Topic, title: str, link: str) -> News:
        """Сохраняет новость в базу данных"""
        news, created = News.objects.get_or_create(title=title, link=link)
        news.topic = topic
        if created:
            log.info(f'Добавлена новость: {news}')
        else:
            news.checked = False
            log.info(f'Повторная проверка новости {news}')
        news.save()
        return news

    @staticmethod
    def _get_topic(topic_name: str) -> Topic:
        """Сохраняет рубрику в базу данных"""
        topic, created = Topic.objects.get_or_create(name=topic_name)
        if created:
            log.info(f'Создана новая рубрика: {topic}')
        return topic

    @classmethod
    def _get_news_block(cls, soup: BeautifulSoup, **kwargs) -> Tag:
        """Возвращает блок новостей за ближайщую дату
        При необходимости есть возможность расширить до выбора даты
        """
        params = {'name': 'div', 'class_': 'news-date'}
        news_on_date = soup.find(**params).find_next_sibling('div', class_='news')
        return news_on_date

    @classmethod
    def _get_soup(cls) -> BeautifulSoup:
        """Инициализация BeautifulSoup объекта"""
        res = requests.get(cls.url)
        return BeautifulSoup(res.content, features="html.parser")

    @staticmethod
    def _get_topic_name(html: BeautifulSoup) -> str:
        """Возвращает наименование рубрики"""
        tag = html.find(name='div', class_='news_i_title-block').find('a', class_='news_lk')
        if tag:
            return tag.text.strip()

    @staticmethod
    def _get_news_list(html: BeautifulSoup) -> list:
        """Возвращает список новостей"""
        return html.find_all('a', attrs={'class': ['news_lst_i_lk news_lk']})


class CheckNews:
    domen = 'https://kodeks.ru'
    months = {
        'Января': 1,
        'Февраля': 2,
        'Марта': 3,
        'Апреля': 4,
        'Мая': 5,
        'Июня': 6,
        'Июля': 7,
        'Августа': 8,
        'Сентября': 9,
        'Октября': 10,
        'Ноября': 11,
        'Декабря': 12,
    }

    def __init__(self):
        self.queryset = None
        self.soup = None
        self.news = None

    def run(self) -> None:
        """Инициализирует проверку непроверенных новостей"""
        self._get_unchecked_news()
        for news in self.queryset:
            self.news = news
            res = self._get_soup(news.link)
            self._update_news(res, news)
            links = self._get_links()
            self._check_links(links)
            news.checked = True
            news.save()

    def _get_unchecked_news(self) -> None:
        """Получение всех непроверенных новостей из базы"""
        self.queryset = News.objects.raw('SELECT "id","link" FROM news_parser_news WHERE checked=false')

    def _get_soup(self, url) -> requests:
        """Инициализация BeautifulSoup объекта"""
        res = requests.get(url)
        self.soup = BeautifulSoup(res.content, features="html.parser")
        return res

    def _update_news(self, res: requests, news: News) -> None:
        """Обновляет поля date и html в экземпляре модели News"""
        news.html = res.text
        news.date = self._get_date(self.soup)
        news.save()
        log.info(f'Новость обновлена {news}')

    @classmethod
    def _get_date(cls, soup: BeautifulSoup) -> datetime:
        """Парсинг даты статьи"""
        date = soup.find('div', class_='date-tx').text
        day, month, year = date.split()
        month = cls.months[month]
        return datetime.date(year=int(year), month=month, day=int(day))

    def _get_links(self) -> list:
        """Получение всех тегов a"""
        return self.soup.find_all('a')

    def _check_links(self, links: list) -> None:
        """Скрипт проверки ссылки"""
        for link_data in links:
            if not link_data.has_attr('href'):
                log.debug(f'{link_data} без ссылки')
                continue
            url = link_data['href']
            if self.url_is_valid(url):
                continue
            log.warning(f'{url} не валиден')
            broken_link, created = BrokenLink.objects.get_or_create(link=url)
            broken_link.news = self.news
            broken_link.save()
            self._change_on_span(url)

    @classmethod
    def url_is_valid(cls, url) -> bool:
        """Проверяет ссылку на валидность"""
        if 'mailto:' in url:
            return True
        elif 'tel:' in url:
            return True
        if 'http' not in url:
            url = cls.domen + url
        try:
            res = requests.get(url)
            return not str(res.status_code).startswith(('4', '5'))
        except (InvalidSchema, InvalidURL, ConnectionError):
            return False

    def _change_on_span(self, url: str) -> None:
        """Заменяет ссылку на тег span"""
        tag = f'<span data="{url}></span>'
        html = self.news.html
        self.news.html = html.replace(url, tag)
        self.news.save()
        log.info(f'{self.news} html обновлен')
