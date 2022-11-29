from pathlib import Path

from django.utils.version import get_version

BASE_DIR = Path(__file__).resolve().parent.parent
APP_DIRS = ['api', 'core', 'recipes', 'users']

assert get_version() > '3.0.0', 'Пожалуйста, используйте версию Django > 3.0.0'

for app_dir in APP_DIRS:
    if not Path(BASE_DIR / app_dir).is_dir():
        assert False, (
            f'В папке проекта {BASE_DIR} не найдено директории '
            f'приложения {app_dir}'
        )

pytest_plugins = ['tests.fixtures.fixture_users']
