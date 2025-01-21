import random
from datetime import datetime, timedelta

import pytest
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

COUNT = 12


@pytest.fixture
def author(django_user_model):
    """
    Фикстура для создания пользователя-автора.

    Создает пользователя с именем 'Автор'.
    """
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    """
    Фикстура для создания пользователя, который не является автором.

    Создает пользователя с именем 'Не автор'.
    """
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    """
    Фикстура для создания клиента, авторизованного как автор.

    Возвращает объект клиента, входящего в систему от имени автора.
    """
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    """
    Фикстура для создания клиента, авторизованного как не автор.

    Возвращает объект клиента, входящего в систему от имени не автора.
    """
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    """
    Фикстура для создания объекта новости.

    Создает и возвращает объект News с заголовком и текстом.
    """
    return News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )


@pytest.fixture
def old_and_new_news():
    """
    Фикстура для создания нескольких новостей.
    Создает и возвращает объекты News с разными датами создания.
    """
    old_news = News.objects.create(
        title='Старая новость',
        text='Текст старой новости',
        date=datetime.now() - timedelta(days=1)
    )
    new_news = News.objects.create(
        title='Новая новость',
        text='Текст новой новости',
        date=datetime.now()
    )
    return [old_news, new_news]


@pytest.fixture
def comment(author, news):
    """
    Фикстура для создания комментария.

    Создает и возвращает объект Comment, связанный с автором и новостью.
    """
    comment_item = Comment.objects.create(
        news=news,
        text='Текст комментария',
        author=author,
    )
    return comment_item


@pytest.fixture
def old_and_new_comments(author, news):
    """
    Фикстура для создания комментария.

    Создает и возвращает объект Comment, связанный с автором и новостью.
    """
    old_comment = Comment.objects.create(
        news=news,
        text='Текст комментария',
        author=author,
        created=datetime.now() - timedelta(days=1)
    )
    new_comment = Comment.objects.create(
        news=news,
        text='Текст комментария',
        author=author,
        created=datetime.now()
    )
    return [old_comment, new_comment]


@pytest.fixture
def form_data():
    """
    Фикстура для создания данных формы.

    Возвращает словарь с текстом комментария.
    """
    return {
        'text': 'Текст',
    }


@pytest.fixture
def multiple_news():
    """Фикстура для создания 12 новостей."""
    news_objects = [
        News(title=f'Заголовок {i + 1}', text=f'Текст новости {i + 1}',
             date=datetime.now() - timedelta(days=i))
        for i in range(COUNT)
    ]
    News.objects.bulk_create(news_objects)
    return news_objects


@pytest.fixture
def random_news(multiple_news):
    """Фикстура для создания случайно перемешанных новостей."""
    shuffled_news = multiple_news
    random.shuffle(shuffled_news)
    return shuffled_news


@pytest.fixture
def multiple_comments(author):
    """Фикстура для создания 12 комментариев."""
    news = News.objects.create(
        title='Новость',
        text='Текст новости',
        date=datetime.now() - timedelta(days=100)
    )
    comment_objects = [
        Comment(news=news, author=author, text=f'Текст комментария {i + 1}',
                created=timezone.now()
                - timedelta(days=i, seconds=random.randint(0, 59)))
        for i in range(COUNT)
    ]
    Comment.objects.bulk_create(comment_objects)
    print(comment_objects)
    return comment_objects


@pytest.fixture
def random_comments(multiple_comments):
    """Фикстура для создания случайно перемешанных комментариев."""
    shuffled_comments = multiple_comments
    random.shuffle(shuffled_comments)
    return shuffled_comments


@pytest.fixture
def urls(news):
    """
    Фикстура для создания нужны URL-адресов.

    Возвращает словари с нужными URL-адресами.
    """
    return {
        'detail': reverse('news:detail', args=[news.pk]),
        'edit': reverse('news:edit', args=[news.pk]),
        'delete': reverse('news:delete', args=[news.pk])
    }