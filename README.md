# Социальная сеть Yatube.
Yatube позволяет публиковать посты и картинки. Комментировать посты других пользователей. Подписываться на любимых авторов и отслеживать их обновления.

### Технологии используемые в проекте:
- Python 3.9.10
- Django 3.2.16
- Pillow 8.3.1
- sorl-thumbnail 12.7.0

Необходимые для работы проекта зависимости описаны в файле requirements.txt

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Mariooooo37/hw05_final
```

```
cd hw05_final
```

Cоздать и активировать виртуальное окружение:

```
python -m venv env
```

```
source env/bin/activate
```

Установить зависимости из файла requirements.txt:

```
python -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```



## Об авторе:
Иванов Роман - студент Яндекс Практикум по курсу Python-разработчик.
