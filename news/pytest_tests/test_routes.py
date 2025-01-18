from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


def test_home_availability_for_anonymous_user(client):
    """
    Проверяет доступность главной страницы для анонимных пользователей.
    
    Ожидается, что статус-код ответа будет 200 (OK).
    """
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_post_availability_for_anonymous_user(client, news):
    """
    Проверяет доступность страницы новостей для анонимных пользователей.
    
    Ожидается, что статус-код ответа будет 200 (OK).
    """
    url = reverse('news:detail', args=[news.pk])
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:delete', 'news:edit')
)
def test_comment_edit_and_delete_only_for_author(author_client, comment, name):
    """
    Проверяет, что только автор комментария может
    его редактировать или удалять.

    Ожидается, что статус-код ответа будет
    200 (OK) для авторизованного автора.
    """
    url = reverse(name, args=[comment.pk])
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('news:delete', 'news:edit')
)
def test_comment_edit_and_delete_for_anonymous_user(client, comment, name):
    """
    Проверяет, что анонимные пользователи не могут
    редактировать или удалять комментарии.

    Ожидается перенаправление анонимного пользователя
    на страницу входа при попытке
    доступа к редактированию или удалению комментария.
    """
    login_url = reverse('users:login')
    url = reverse(name, args=[comment.pk])
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'name',
    ('news:delete', 'news:edit')
)
def test_comment_edit_and_delete_not_for_author(not_author_client,
                                                comment, name):
    """
    Проверяет, что пользователи, не являющиеся авторами комментария,
    не могут его редактировать или удалять.
    
    Ожидается, что статус-код ответа будет 404 (Not Found).
    """
    url = reverse(name, args=[comment.pk])
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND


@pytest.mark.parametrize(
    'name',
    ('users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    """
    Проверяет доступность страниц входа, выхода
    и регистрации для анонимных пользователей.

    Ожидается, что статус-код ответа будет 200 (OK).
    """
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK