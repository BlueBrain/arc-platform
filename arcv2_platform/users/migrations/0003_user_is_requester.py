# Generated by Django 3.0 on 2020-05-11 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_is_switch_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_requester',
            field=models.BooleanField(default=False),
        ),
    ]
