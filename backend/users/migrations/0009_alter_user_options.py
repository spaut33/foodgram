# Generated by Django 3.2.16 on 2022-12-03 16:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_auto_20221202_1922'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ('-id',)},
        ),
    ]
