from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


@pytest.mark.usefixtures('news')
def test_anonymous_user_cant_create_comment(client, form_data, urls):
    """
    Проверяет, что анонимные пользователи не могут создавать комментарии.

    Ожидается, что при попытке отправить комментарий анонимным пользователем
    произойдет перенаправление на страницу входа с параметром next,
    указывающим на подробности новости. Также ожидается, что количество
    комментариев в базе данных останется равным изначальному количеству.
    """
    comment_count = Comment.objects.count()
    response = client.post(urls['detail'], data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={urls["detail"]}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == comment_count


def test_user_can_create_comment(author_client, form_data, news, author, urls):
    """
    Проверяет, что авторизованные пользователи могут создавать комментарии.

    Ожидается, что при отправке корректного комментария авторизованным
    пользователем произойдет перенаправление на страницу новостей с
    якорем #comments. Также проверяется, что созданный комментарий
    соответствует отправленным данным.
    """
    response = author_client.post(urls['detail'], data=form_data)
    assertRedirects(response, reverse('news:detail',
                                      kwargs={'pk': news.pk}) + '#comments')
    assert Comment.objects.count() == 1
    new_comment = Comment.objects.get()
    assert new_comment.text == form_data['text']
    assert new_comment.author == author


@pytest.mark.usefixtures('news')
def test_comment_with_bad_words_is_not_published(author_client, urls):
    """
    Проверяет, что комментарии с нецензурной лексикой не публикуются.

    При отправке комментария, содержащего неподобающие слова,
    ожидается, что комментарий не будет сохранен в базе данных
    и форма вернет сообщение об ошибке.
    """
    bad_comment_data = {
        'text': f'Я не согласен, ты {BAD_WORDS}!',
    }
    response = author_client.post(urls['detail'], data=bad_comment_data)
    assert Comment.objects.filter(text=bad_comment_data['text']).count() == 0
    assert response.context['form'].errors['text'] == [WARNING]


def test_only_author_can_edit_comment(author_client, comment, urls):
    """
    Проверяет, что только автор комментария может его редактировать.

    Ожидается, что авторизованный пользователь, который является
    автором комментария, сможет изменить текст комментария без ошибок.
    """
    new_data = {
        'text': 'Отредактированный текст комментария.',
    }
    response = author_client.post(urls['edit'], data=new_data)
    assert response.status_code == HTTPStatus.FOUND
    comment.refresh_from_db()
    assert comment.text == new_data['text']


def test_not_author_cannot_edit_other_comment(not_author_client, comment,
                                              urls):
    """
    Проверяет, что неавторизованный пользователь
    не может редактировать чужой комментарий.

    Ожидается, что когда не автор комментария пытается его отредактировать,
    будет возвращен статус 404, и текст комментария останется прежним.
    """
    new_data = {
        'text': 'Отредактированный текст комментария.',
    }
    response = not_author_client.post(urls['edit'], data=new_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text != new_data['text']
    assert comment.author != not_author_client


def test_only_author_can_delete_comment(author_client, comment, urls):
    """
    Проверяет, что только автор комментария может его удалить.

    Ожидается, что автор комментария сможет удалить его, и
    количество комментариев в базе данных уменьшится до нуля.
    """
    response = author_client.post(urls['delete'])
    assert response.status_code == HTTPStatus.FOUND
    assert not Comment.objects.filter(pk=comment.pk).exists()


def test_user_cannot_delete_other_comment(not_author_client, comment, urls):
    """
    Проверяет, что авторизованный пользователь
    не может удалить чужой комментарий.

    Ожидается, что при попытке удалить комментарий, не являясь его автором,
    вернется статус 404, а количество комментариев останется прежним.
    """
    response = not_author_client.post(urls['delete'])
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.filter(pk=comment.pk).exists()
