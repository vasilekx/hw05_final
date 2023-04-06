# Yatube - социальная сеть блогеров

## Описание
Пользователи могут создать учетную запись, публиковать записи, подписываться на любимых авторов и комментировать понравившиеся записи. Проект реализован на Django. 

Также разработан [API для проекта](https://github.com/vasilekx/api_final_yatube) на Django REST framework(DRF). API разрешает аутентифицированным пользователям управлять собственным  контентом. Аутентификация реализована по JWT-токену.

## Применяемые технологи

[![Python](https://img.shields.io/badge/Python-3.7-blue?style=flat-square&logo=Python&logoColor=3776AB&labelColor=d0d0d0)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-2.2.16-blue?style=flat-square&logo=Django&logoColor=3776AB&labelColor=d0d0d0)](https://docs.djangoproject.com/en/2.2/)
[![Pillow](https://img.shields.io/badge/Pillow-8.3.1-blue?style=flat-square&logoColor=3776AB&labelColor=d0d0d0)](https://pillow.readthedocs.io/en/stable/)
[![SQLite3](https://img.shields.io/badge/SQLite-3-blue?style=flat-square&logo=SQLite&logoColor=3776AB&labelColor=d0d0d0)](https://www3.sqlite.org/index.html)

---

## Запуск сервиса

Клонировать репозиторий и перейти в него в командной строке:

```bash
git clone git@github.com:vasilekx/hw05_final.git
```

```bash
cd hw05_final
```

Создать и активировать виртуальное окружение:

```bash
python3 -m venv venv
```

* Если у вас Linux/MacOS

    ```bash
    source venv/bin/activate
    ```

* Если у вас windows

    ```bash
    source venv/scripts/activate
    ```

Установить зависимости из файла requirements.txt:

```bash
python3 -m pip install --upgrade pip
```

```bash
pip install -r requirements.txt
```

Выполнить миграции:

```bash
python3 manage.py migrate
```

Запустить проект:

```bash
python3 manage.py runserver
```

Создайте пользователя с правами администратора:
```bash
python3 manage.py createsuperuser
```
---

## Доступ по адресу
```
http://127.0.0.1:8000
```


## Автор проекта
[Владислав Василенко](https://github.com/vasilekx)
