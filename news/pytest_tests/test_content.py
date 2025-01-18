import pytest
from django.urls import reverse

from news.models import Comment, News

pytestmark = pytest.mark.django_db


def test_news_count_on_home_page(author_client):
    """
    Проверяет, что на главной странице количество новостей не превышает 10.

    Создает 12 новостей и затем запрашивает главную страницу. 
    Ожидается, что количество новостей в контексте не превысит 10.
    """
    for i in range(12):
        News.objects.create(title=f'Заголовок {i}', text=f'Текст новости {i}')
    response = author_client.get(reverse('news:home'))
    assert len(response.context['news_feed']) <= 10


def test_news_sorted_by_creation_date(client, news):
    """
    Проверяет, что новости сортируются по дате создания.

    Создает новую новость и запрашивает главную страницу.
    Ожидается, что самая первая новость в контексте - это
    старая новость, а вторая - новая.
    """
    news
    News.objects.create(title='Новый заголовок', text='Текст свежей новости')
    response = client.get(reverse('news:home'))
    assert response.context['news_feed'][0].title == 'Заголовок'
    assert response.context['news_feed'][1].title == 'Новый заголовок'


def test_comments_sorted_by_creation_date(author_client, comment):
    """
    Проверяет, что комментарии сортируются по дате создания.

    Создает новый комментарий и запрашивает страницу с новостью. 
    Ожидается, что комментарии будут возвращены в правильном порядке.
    """
    comment
    Comment.objects.create(news=comment.news, text='Текст нового комментария',
                           author=comment.author)
    response = author_client.get(reverse('news:detail',
                                         args=(comment.news.pk,)))
    comments = response.context['object'].comment_set.all()
    assert comments[0].text == 'Текст комментария'
    assert comments[1].text == 'Текст нового комментария'


def test_anonymous_user_not_see_comment_form(client, news):
    """
    Проверяет, что анонимные пользователи не видят форму комментария.

    Запрашивает страницу с новостью и проверяет, что форма
    не присутствует в контексте.
    """
    response = client.get(reverse('news:detail', args=(news.pk,)))
    assert 'form' not in response.context


def test_authorized_user_can_see_comment_form(not_author_client, news):
    """
    Проверяет, что авторизованные пользователи видят форму комментария.

    Запрашивает страницу с новостью и проверяет, что форма 
    присутствует в контексте.
    """
    response = not_author_client.get(reverse('news:detail', args=(news.pk,)))
    assert 'form' in response.context
