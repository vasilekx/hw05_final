# Generated by Django 2.2.16 on 2022-01-21 21:19

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0012_comment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'verbose_name': 'Пост', 'verbose_name_plural': 'Посты'},
        ),
        migrations.RemoveField(
            model_name='post',
            name='pub_date',
        ),
        migrations.AddField(
            model_name='post',
            name='created',
            field=models.DateTimeField(auto_now_add=True, default=datetime.datetime(2022, 1, 21, 21, 19, 56, 366912), help_text='Дата создания будет автоматически установлена в текущую дату при создании', verbose_name='Дата создания'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='comment',
            name='created',
            field=models.DateTimeField(auto_now_add=True, help_text='Дата создания будет автоматически установлена в текущую дату при создании', verbose_name='Дата создания'),
        ),
    ]
