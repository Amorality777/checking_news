Реализован парсер новостей https://kodeks.ru/news.
Функционал:
1. По ссылке \<domen>/cheking/ Запускается задача получения списка новостей за последний день, и проверка на валидность ссылок внутри (+ замена ссылок на span)
2. По ссылке \<domen>/report/ Реализуется отчет по всем неработающим ссылкам со значением fixed = False


Для запуска проекта\n
Необходимо установить docker-compose\n
Выполнить следующие операции:
pip install -r req.txt
python manage.py makemigrations
python manage.py migrate
sudo docker-compose up
celery -A screenshot_service worker -l INFO --pool=solo
python manage.py runserver
