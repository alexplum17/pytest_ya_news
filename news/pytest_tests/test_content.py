from datetime import timedelta

import pytest
from django.urls import reverse

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures('multiple_news')
def test_news_count_on_home_page(author_client):
    """
    Проверяет, что на главной странице количество новостей не превышает 10.
    Создает 12 новостей и затем запрашивает главную страницу.
    Ожидается, что количество новостей в контексте не превысит 10.
    """
    response = author_client.get(reverse('news:home'))
    assert response.context['object_list'].count() <= 10

@pytest.mark.usefixtures('random_news')
def test_news_sorted_by_creation_date(client):
    """
    Проверяет, что новости сортируются по дате создания.
    Ожидается, что самая старая новость в контексте - это
    последняя новость в списке новостей, а самая новая -
    первая в списке новостей.
    """
    response = client.get(reverse('news:home'))
    news_list = list(response.context['object_list'])
    assert news_list[0].date > news_list[1].date
    for i in range(1, len(news_list) - 1):
        assert news_list[i].date > news_list[i + 1].date
    assert news_list[-1].date < news_list[0].date


@pytest.mark.usefixtures('random_comments')
def test_comments_sorted_by_creation_date(author_client, multiple_comments):
    """
    Проверяет, что комментарии сортируются по дате создания.
    Ожидается, что самый старый комментарий в контексте - это
    первый комментарий в списке комментариев, а самый новый -
    последний в списке комментарией.
    Создает новый комментарий и запрашивает страницу с новостью.
    Ожидается, что комментарии будут возвращены в правильном порядке.
    """
    response = author_client.get(reverse('news:detail',
                                         args=(multiple_comments[0].news.pk,)))
    comment_list = list(response.context['object'].comment_set.all())
    assert comment_list[0].created < comment_list[1].created
    for i in range(1, len(comment_list) - 1):
        assert comment_list[i].created < comment_list[i + 1].created
    assert comment_list[-1].created > comment_list[0].created


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
    assert isinstance(response.context['form'], CommentForm)
