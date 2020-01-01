# Generated by Django 3.0.1 on 2020-01-01 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='category',
            name='calendar',
        ),
        migrations.AddField(
            model_name='calendar',
            name='categories',
            field=models.ManyToManyField(to='event.Category'),
        ),
    ]
