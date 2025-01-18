import pytest
from django.test.client import Client

from news.models import Comment, News


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
    news_item = News.objects.create(
        title='Заголовок',
        text='Текст новости',
    )
    return news_item


@pytest.fixture
def comment(author, news):
    """
    Фикстура для создания комментария.

    Создает и возвращает объект Comment, связанный с автором и новостью.
    """
    comment_item = Comment.objects.create(
        news=news,
        text='Текст комментария',
        author=author
    )
    return comment_item


@pytest.fixture
def pk_for_args(news):
    """
    Фикстура для получения первичного ключа новости.

    Возвращает кортеж с первичным ключом объекта news.
    """
    return (news.pk,)


@pytest.fixture
def form_data():
    """
    Фикстура для создания данных формы.

    Возвращает словарь с текстом комментария.
    """
    return {
        'text': 'Текст',
    }
