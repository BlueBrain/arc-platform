# Generated by Django 3.0 on 2020-05-01 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matchmaking', '0003_match_status_reason'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='status',
            field=models.CharField(choices=[('attributed', 'Attributed'), ('on_hold', 'On hold'), ('rejected', 'Rejected'), ('validated', 'Validated')], default='attributed', max_length=20),
        ),
    ]
