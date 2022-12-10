# 🍝 [Foodgram - кулинарный помощник](https://foodgram.telfia.com/)
![ci workflow](https://github.com/spaut33/foodgram-project-react/actions/workflows/foodgram_workflow.yaml/badge.svg) [![codecov](https://codecov.io/github/spaut33/foodgram-project-react/branch/master/graph/badge.svg?token=UAKLFBKQ17)](https://codecov.io/github/spaut33/foodgram-project-react) [![Codacy Badge](https://app.codacy.com/project/badge/Grade/0e17512670a945a4bfe33c732c73ec75)](https://www.codacy.com?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=spaut33/foodgram-project-react&amp;utm_campaign=Badge_Grade) ![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django) ![Django](https://img.shields.io/badge/Django-3.2-green) ![DRF](https://img.shields.io/badge/DRF-3.12.4-green) 

На этом сервисе пользователи могут публиковать кулинарные рецепты, подписываться 
публикации других пользователей, добавлять понравившиеся рецепты в список 
«Избранное», а перед походом в магазин скачивать сводный список продуктов, 
необходимых для приготовления одного или нескольких выбранных блюд.

## Содержание

- [Описание](#-описание)
- [Описание приложения](#Описание-приложения)
- [Установка и запуск](#%EF%B8%8F-установка-и-запуск)
- [Использованные технологии](#%EF%B8%8F-использованные-технологии)
- [Лицензия](#%EF%B8%8F-лицензия)
- [Автор](#-автор)


# 📖 Описание

Это готовый Docker-образ, содержащий REST API бекэнд и SPA-фронтенд на React. 
Пользователи могут:
- регистрироваться в приложении;
- получать токен для полноценного доступа к сайту;
- авторизованные пользователи могут создавать рецепты, добавлять их в избранное, подписываться на других пользователей, добавлять рецепты в список покупок;
- администраторы через специальный интерфейс могут создавать новых пользователей, изменять учетные данные других пользователей, редактировать ингредиенты, теги, рецепты;
- пользователи могут фильтровать рецепты по тегам, авторам.

Сайт приложения: [Foodgram](https://foodgram.telfia.com/)

### Описание приложения

Разделы сайта имеют разграниченный доступ. Пользователи делятся на:
- неавторизованных пользователей
- зарегистрированных пользователей (авторов)
- администраторов

Авторы могут создавать новые рецепты, редактировать и удалять их. Администраторы могут временно блокировать пользователей.
При создании рецепта, авторы могут добавлять изображение, ингредиенты и их количество из готового списка, назначать теги.
Пользователи могут добавлять рецепты в список покупок и скачивать список в виде PDF-файла.

## 🛠️ Установка и запуск

Для запуска приложения должен быть установлен [git](https://git-scm.com/) и [docker](https://www.docker.com/).

```bash
git clone git@github.com:spaut33/foodgram-project-react.git
cd foodgram-project-react
```

Шаблон для создания .env файла (содержит необходимые для работы перменные окружения). Данный файл должен находится в папке `infra` проекта:
```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY=django-secret-key
ALLOWED_HOSTS="127.0.0.1"
DEBUG=True
```

Собрать и запустить контейнеры
```bash
cd infra
sudo docker-compose ud -d --build
```

После запуска контейнеров необходимо применить миграции, создать суперпользователя и собрать статику:
```bash
sudo docker-compose exec backend python manage.py migrate
sudo docker-compose exec backend python manage.py createsuperuser
sudo docker-compose exec backend python manage.py collectstatic --no-input
```

### Тесты

Для запуска тестов нужно перейти в директорию репозитория

```bash
cd backend
```

Cоздать и активировать виртуальное окружение:

```bash
python -m venv .venv
source env/bin/activate
```

Запустить тесты:

```bash
pytest
```

Для наполнения базы данных данными можно использовать команду:

```bash
sudo docker-compose exec web python3 manage.py flush --no-input
sudo docker-compose exec web python3 manage.py loaddata fixtures.json
```

## ⚙️ Использованные технологии

- [Python 3.8](https://www.python.org/)
- [Django 3.2](https://www.djangoproject.com/)
- [Django Rest Framework 3.12](https://www.django-rest-framework.org/)
- [Djoser](https://djoser.readthedocs.io/en/latest/)
- [django-filter](https://github.com/carltongibson/django-filter/)
- [django-colorfield](https://pypi.org/project/django-colorfield/)
- [python-dotenv](https://github.com/theskumar/python-dotenv)
- [drf-yasg](https://github.com/axnsan12/drf-yasg)
- [pytest](https://docs.pytest.org/)
- [Docker](https://docker.com/)
- [PostgreSQL](https://www.postgresql.org/)
- [Nginx](https://www.nginx.com/)
    
## ⚠️ Лицензия

[MIT](https://choosealicense.com/licenses/mit/)

## 🧑‍💻 Автор

- [Роман Петраков](https://www.github.com/spaut33)

