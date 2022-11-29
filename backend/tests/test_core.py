import json
from pathlib import Path

import pytest
from core.management.commands.load_ingredients import Command
from django.core.management.base import BaseCommand, CommandError


def test_wrong_path(mocker):
    """Отсутствующий или неверный путь к файлу выбрасывает исключение"""
    path = Path(__file__).resolve() / 'wrong_path' / 'ingredients.json'
    mocker.patch('core.management.commands.load_ingredients.Command.make_path', return_value=path)  # Or "src.os.path.join"
    with pytest.raises(CommandError) as e:
        Command().handle()

@pytest.mark.django_db(transaction=True)
def test_wrong_json_content(mocker, capfd):
    """"Если в json-файле один из элементов неверный"""
    mocker.patch('json.loads', return_value=[{'wrong_item': 'г'}, {'name': 'абрикосовое пюре', 'measurement_unit': 'г'}])
    Command().handle()
    out, err = capfd.readouterr()
    assert out.strip() == (
        'Команда выполнена успешно. '
        'Найдено 1 ингредиентов. Из них новых '
        '1 добавлено в базу данных.'
    ), 'Неверное количество обработанных элементов'

@pytest.mark.django_db(transaction=True)
def test_wrong_json_content(mocker, capfd):
    """Если json пустой"""
    mocker.patch('json.loads', return_value=[])
    Command.handle()


