# Generated by Django 3.0.1 on 2020-01-02 16:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0015_auto_20200102_1700'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calendar',
            name='slug',
            field=models.SlugField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='location',
            name='slug',
            field=models.SlugField(blank=True, null=True),
        ),
    ]
