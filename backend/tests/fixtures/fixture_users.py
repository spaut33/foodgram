import pytest
from django.contrib.auth import get_user_model


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        username='test_user',
        email='test.user@fake.mail',
        password='123456Qq'
    )

@pytest.fixture
def another_user(django_user_model):
    return django_user_model.objects.create_user(
        username='another_test_user',
        email='another.test.user@fake.mail',
        password='123456Qq'
    )

@pytest.fixture
def admin(django_user_model):
    return django_user_model.objects.create_user(
        username='test_admin',
        email='test.admin@fake.mail',
        password='123456Qq',
        is_superuser=True
    )


@pytest.fixture
def token_admin(admin):
    from rest_framework.authtoken.models import Token

    token = Token.objects.create(user_id=user.id)
    return {'access': str(token)}


@pytest.fixture
def admin_client(token_admin):
    from rest_framework.test import APIClient

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token_admin["access"]}')
    return client


@pytest.fixture
def token_user(user):
    from rest_framework.authtoken.models import Token

    token = Token.objects.create(user_id=user.id)
    return {'access': str(token)}


@pytest.fixture
def user_client(token_user):
    from rest_framework.test import APIClient

    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token_user["access"]}')
    return client


@pytest.fixture(
    params=[
        pytest.param(1, id='1 user'),
        pytest.param(2, id='2 users'),
        pytest.param(3, id='3 users'),
    ]
)

def some_users(request):
    return [
        get_user_model().objects.create_user(
            username=f'test_user_{i}',
            email=f'test.user{i}@fake.mail',
            password='123456Qq',
            role='user',
        )
        for i in range(request.param)
    ]
