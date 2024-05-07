### Проект Продуктовый помощник

# Описание
Проект "Продуктовый помощник" - проект, который позволяет создавать архив собственных рецептов. Он позволяет решать следующие задачи:
- сохранение созданных записей рецептов блюд с указанием их ингредиентов, изображений, описаний, а также категоризацией по отдельным группам;
- сортировка уже сохраненных рецептов по группам;
- загрузка списка ингредиентов блюд, которые добавлены в корзину.

В проекте реализованы следующие модули:
- Пользователи,
- Рецепты,
- Модуль REST API.

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone git@github.com:AlexeyADavydov/recipes-manager-project.git
```


В папке /infra создайте файл .env со следующими переменными:
'''
POSTGRES_DB=foodgram
POSTGRES_USER=foodgram_user
POSTGRES_PASSWORD=foodgram_password
DB_NAME=foodgram

DB_HOST=db
DB_PORT=5432
'''

Через эту же папку выполните команду
'''
sudo docker compose up -d
'''

Скопируйте статику и убедитесь, что её местонахождение соответствует найтройкам nginx.conf.
'''
sudo docker compose -f docker-compose.yml run backend python manage.py import_ingredients_csv ingredients.csv

sudo docker compose -f docker-compose.production.yml run backend cp -r /app/collected_static/. /backend_static/static/

'''

Загрузите данные ингредиентов:
'''
sudo docker compose -f docker-compose.yml run backend python manage.py import_ingredients_csv ingredients.csv

'''

Настройте при необходимости параметры nginx и перезагрузите его: 
'''
sudo nano /etc/nginx/sites-enabled/default 

sudo service nginx reload
'''

# Проект размещен на сайте: alexeyadavydov.com

# Доступ в админку
'''
Login - admin
Email: admin@admin.ru
Password: admin
'''

Certbot