import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from django.conf import settings

from recipes.models import Ingredient, Unit


class Command(BaseCommand):
    help = 'Импорт ингредиентов из JSON.'

    def handle(self, *args, **options):
        path_to_file = settings.BASE_DIR / '..' / 'data' / 'ingredients.json'
        if not Path.is_file(path_to_file):
            raise CommandError(f'Файл {path_to_file} не найден.')
        with open(path_to_file, encoding='utf-8') as data_file:
            data = json.loads(data_file.read())
            objects = []
            current_objects_count = Ingredient.objects.count()
            for item in data:
                item['measurement_unit'], _ = Unit.objects.get_or_create(
                    name=item['measurement_unit']
                )
                objects.append(Ingredient(**item))
                found_objects = len(objects)
            try:
                Ingredient.objects.bulk_create(objects, ignore_conflicts=True)
                new_amount = Ingredient.objects.count() - current_objects_count
            except Exception as e:
                print(f'Ошибка во время заполнения базы данных значениями {e}')
            else:
                print(
                    f'Команда выполнена успешно. '
                    f'Найдено {found_objects} ингредиентов. Из них новых '
                    f'{new_amount} добавлено в базу данных.'
                )
