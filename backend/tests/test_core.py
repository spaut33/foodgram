from pathlib import Path

import pytest

from core.management.commands.load_ingredients import Command
from django.core.management.base import CommandError


@pytest.fixture
def wrong_json():
    return [
        {'wrong_item': 'г'},
        {'name': 'абрикосовое пюре', 'measurement_unit': 'г'},
    ]


def test_wrong_path(mocker):
    """Отсутствующий или неверный путь к файлу выбрасывает исключение"""
    path = Path(__file__).resolve() / 'wrong_path' / 'ingredients.json'
    mocker.patch(
        'core.management.commands.load_ingredients.Command.make_path',
        return_value=path,
    )
    with pytest.raises(CommandError) as e:
        Command().handle()


@pytest.mark.django_db(transaction=True)
def test_corrupted_file(mocker):
    """Отсутствующий или неверный путь к файлу выбрасывает исключение"""
    mocked_json_file = mocker.mock_open(read_data='not a json at all {{}}')
    mocker.patch('builtins.open', mocked_json_file)
    with pytest.raises(ValueError) as e:
        Command().handle()


@pytest.mark.django_db(transaction=True)
def test_wrong_json_content(mocker, capfd, wrong_json):
    """"Если в json-файле один из элементов неверный, должны быть обработаны
    только верные элементы"""
    mocker.patch('json.loads', return_value=wrong_json)
    Command().handle()
    out, err = capfd.readouterr()
    assert out.strip() == (
        'Команда выполнена успешно. '
        'Найдено 1 ингредиентов. Из них новых '
        '1 добавлено в базу данных.'
    ), 'Неверное количество обработанных элементов'


@pytest.mark.django_db(transaction=True)
def test_empty_json(mocker, capfd):
    """Если json пустой"""
    mocker.patch('json.loads', return_value=[])
    Command().handle()
    out, err = capfd.readouterr()
    assert out.strip() == (
        'Команда выполнена успешно. '
        'Найдено 0 ингредиентов. Из них новых '
        '0 добавлено в базу данных.'
    ), 'Ошибка при обработке пустого json-файла'


@pytest.mark.django_db(transaction=True)
def test_not_created_item(mocker, capfd):
    """Тест ошибки при добавлении итемов в базу данных"""
    mocker.patch(
        'django.db.models.query.QuerySet.bulk_create',
        side_effect=Exception('mocked error'),
    )
    Command().handle()
    out, err = capfd.readouterr()
    assert out.strip() == (
        f'Ошибка во время заполнения базы данных значениями mocked error'
    )
