# Generated by Django 3.2.16 on 2022-12-02 16:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_subscription_date_added'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscription',
            options={'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
        migrations.AlterField(
            model_name='subscription',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='subscriptions', to=settings.AUTH_USER_MODEL, verbose_name='Подписчик'),
        ),
    ]