from checking_news.celery import app
from .services import NewsParser, CheckNews
from logs.settings import setup_logger

log = setup_logger()


@app.task(name='parse')
def parse():
    log.info('Запущена новая задача')
    NewsParser.run()
    checker = CheckNews()
    checker.run()
