import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from logs.settings import setup_logger
from news_parser.models import Topic, News

log = setup_logger()


class NewsParser:
    url = 'https://kodeks.ru/news'

    @classmethod
    def get_news_on_last_date(cls):
        soup = cls._get_soup()
        news_block = cls._get_news_block(soup)
        news_blocks = news_block.find_all('div', attrs={'class': ['news_i ', 'news_tile']}, recursive=False)
        for topic_data in news_blocks:
            topic_name = cls._get_topic_name(topic_data)
            topic = cls._get_topic(topic_name)
            news_list = cls._get_news(topic_data)
            for news in news_list:
                title = news.text.strip()
                link = news["href"]
                news = cls._get_news(topic, title, link)

    @staticmethod
    def _get_news(topic, title, link):
        news, created = News.objects.get_or_create(topic=topic, title=title, link=link)
        if created:
            log.info(f'Добавлена новость: {news}')
        else:
            news.checked = False
            news.save()
            log.info(f'Повторная проверка новости {news}')
        return news

    @staticmethod
    def _get_topic(topic_name):
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
    def _get_news(html: BeautifulSoup) -> list:
        """Возвращает список новостей"""
        return html.find_all('a', attrs={'class': ['news_lst_i_lk news_lk']})


NewsParser.get_news_on_last_date()
