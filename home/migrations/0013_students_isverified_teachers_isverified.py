# Generated by Django 4.0.3 on 2022-04-20 23:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0012_quentions_correntanswer_quentions_isfixed'),
    ]

    operations = [
        migrations.AddField(
            model_name='students',
            name='isVerified',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='teachers',
            name='isVerified',
            field=models.BooleanField(default=False),
        ),
    ]
