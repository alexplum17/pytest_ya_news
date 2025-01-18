from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, form_data, news):
    """
    Проверяет, что анонимные пользователи не могут создавать комментарии.

    Ожидается, что при попытке отправить комментарий анонимным пользователем
    произойдет перенаправление на страницу входа с параметром next, 
    указывающим на подробности новости. Также ожидается, что количество
    комментариев в базе данных останется равным нулю.
    """
    url = reverse('news:detail', args=[news.pk])
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_can_create_comment(author_client, form_data, news, author):
    """
    Проверяет, что авторизованные пользователи могут создавать комментарии.

    Ожидается, что при отправке корректного комментария авторизованным 
    пользователем произойдет перенаправление на страницу новостей с
    якорем #comments. Также проверяется, что созданный комментарий
    соответствует отправленным данным.
    """
    url = reverse('news:detail', args=[news.pk])
    response = author_client.post(url, data=form_data)
    assertRedirects(response, reverse('news:detail', kwargs={'pk': news.pk}) + '#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


def test_comment_with_bad_words_is_not_published(author_client, news):
    """
    Проверяет, что комментарии с нецензурной лексикой не публикуются.

    При отправке комментария, содержащего неподобающие слова, 
    ожидается, что комментарий не будет сохранен в базе данных
    и форма вернет сообщение об ошибке.
    """
    bad_comment_data = {
        'text': f'Я не согласен, ты {BAD_WORDS}!',
    }
    url = reverse('news:detail', args=[news.pk])
    response = author_client.post(url, data=bad_comment_data)
    assert Comment.objects.filter(text=bad_comment_data['text']).count() == 0
    assert response.context['form'].errors['text'] == [WARNING]


def test_only_author_can_edit_comment(author_client, comment):
    """
    Проверяет, что только автор комментария может его редактировать.

    Ожидается, что авторизованный пользователь, который является
    автором комментария, сможет изменить текст комментария без ошибок.
    """
    url = reverse('news:edit', args=[comment.pk])
    new_data = {
        'text': 'Отредактированный текст комментария.',
    }
    response = author_client.post(url, data=new_data)
    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == new_data['text']


def test_not_author_cannot_edit_other_comment(not_author_client, comment):
    """
    Проверяет, что неавторизованный пользователь не может редактировать чужой комментарий.

    Ожидается, что когда не автор комментария пытается его отредактировать,
    будет возвращен статус 404, и текст комментария останется прежним.
    """
    url = reverse('news:edit', args=[comment.pk])
    new_data = {
        'text': 'Отредактированный текст комментария.',
    }
    response = not_author_client.post(url, data=new_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != new_data['text']


def test_only_author_can_delete_comment(author_client, comment):
    """
    Проверяет, что только автор комментария может его удалить.

    Ожидается, что автор комментария сможет удалить его, и
    количество комментариев в базе данных уменьшится до нуля.
    """
    url = reverse('news:delete', args=[comment.pk])
    response = author_client.post(url)
    assert response.status_code == HTTPStatus.FOUND
    assert Comment.objects.count() == 0


def test_only_author_cannot_delete_other_comment(not_author_client, comment):
    """
    Проверяет, что неавторизованный пользователь не может удалить чужой комментарий.

    Ожидается, что при попытке удалить комментарий, не являясь его автором, 
    вернется статус 404, а количество комментариев останется прежним.
    """
    url = reverse('news:delete', args=[comment.pk])
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
