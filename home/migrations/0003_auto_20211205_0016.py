# Generated by Django 3.2.9 on 2021-12-04 18:46

import datetime
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_auto_20211205_0010'),
    ]

    operations = [
        migrations.CreateModel(
            name='Answers',
            fields=[
                ('aID', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('ans', models.TextField()),
                ('dateTimeOfPost', models.DateTimeField(default=datetime.datetime(2021, 12, 5, 0, 16, 24, 69384))),
                ('likeCount', models.IntegerField(default=0)),
                ('disLikeCount', models.IntegerField(default=0)),
            ],
        ),
        migrations.AlterField(
            model_name='quentions',
            name='dateTimeOfPost',
            field=models.DateTimeField(default=datetime.datetime(2021, 12, 5, 0, 16, 24, 69384)),
        ),
        migrations.AlterField(
            model_name='students',
            name='dateTimeOfJoin',
            field=models.DateTimeField(default=datetime.datetime(2021, 12, 5, 0, 16, 24, 9565)),
        ),
        migrations.AlterField(
            model_name='teachers',
            name='dateTimeOfJoin',
            field=models.DateTimeField(default=datetime.datetime(2021, 12, 5, 0, 16, 24, 69384)),
        ),
    ]