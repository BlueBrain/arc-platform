# Generated by Django 3.0 on 2020-04-23 10:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('resources', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Supply',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_time', models.DateTimeField(auto_now_add=True)),
                ('fullname', models.CharField(max_length=100)),
                ('role', models.CharField(max_length=100)),
                ('affiliation', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=25)),
                ('author_comment', models.TextField(blank=True, max_length=500)),
                ('update_time', models.DateTimeField(auto_now=True)),
                ('quantity', models.PositiveIntegerField()),
                ('comment', models.TextField(blank=True, max_length=400)),
                ('status', models.CharField(choices=[('available', 'Available'), ('ongoing_attribution', 'Ongoing attribution'), ('attributed', 'Attributed'), ('archived', 'Archived'), ('closed', 'Closed')], default='available', max_length=20)),
                ('company', models.CharField(blank=True, max_length=100)),
                ('street_name', models.CharField(blank=True, max_length=100)),
                ('street_number', models.CharField(blank=True, max_length=20)),
                ('city', models.CharField(blank=True, max_length=50)),
                ('zip', models.PositiveIntegerField(blank=True, null=True)),
                ('item_catalog_number', models.CharField(blank=True, max_length=50)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='resources.Category')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_supplies', to=settings.AUTH_USER_MODEL)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='resources.CategoryItem')),
                ('resource', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='resources.Resource')),
                ('resourceType', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='resources.ResourceType')),
                ('updater', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='updated_supplies', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Supplies',
                'ordering': ['-creation_time'],
            },
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_time', models.DateTimeField(auto_now_add=True)),
                ('fullname', models.CharField(max_length=100)),
                ('role', models.CharField(max_length=100)),
                ('affiliation', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(max_length=25)),
                ('author_comment', models.TextField(blank=True, max_length=500)),
                ('update_time', models.DateTimeField(auto_now=True)),
                ('quantity', models.PositiveIntegerField()),
                ('comment', models.TextField(blank=True, max_length=400)),
                ('status', models.CharField(choices=[('open', 'Open'), ('closed', 'Closed'), ('archived', 'Archived')], default='open', max_length=10)),
                ('priority', models.CharField(choices=[('critical', 'Critical'), ('high', 'High'), ('medium', 'Medium'), ('low', 'Low')], default='medium', max_length=10)),
                ('sensitive', models.BooleanField(default=False)),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='resources.Category')),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_requests', to=settings.AUTH_USER_MODEL)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='resources.CategoryItem')),
                ('resource', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='resources.Resource')),
                ('resourceType', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='resources.ResourceType')),
                ('updater', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='updated_requests', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Requests',
                'ordering': ['-creation_time'],
            },
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_time', models.DateTimeField(auto_now_add=True)),
                ('quantity', models.PositiveIntegerField()),
                ('status', models.CharField(choices=[('attributed', 'Attributed'), ('validated', 'Validated')], default='attributed', max_length=20)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_matches', to=settings.AUTH_USER_MODEL)),
                ('request', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='matches', to='matchmaking.Request')),
                ('supply', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='matches', to='matchmaking.Supply')),
                ('validator', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='validated_matches', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]