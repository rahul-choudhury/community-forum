# Generated by Django 3.2.9 on 2021-12-08 14:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_auto_20211207_2240'),
    ]

    operations = [
        migrations.RenameField(
            model_name='students',
            old_name='dislikeRecord',
            new_name='answerRecord',
        ),
        migrations.RenameField(
            model_name='students',
            old_name='likeRecord',
            new_name='questionRecord',
        ),
        migrations.RenameField(
            model_name='teachers',
            old_name='dislikeRecord',
            new_name='answerRecord',
        ),
        migrations.RenameField(
            model_name='teachers',
            old_name='likeRecord',
            new_name='questionRecord',
        ),
    ]
