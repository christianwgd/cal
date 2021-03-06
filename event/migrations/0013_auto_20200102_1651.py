# Generated by Django 3.0.1 on 2020-01-02 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0012_auto_20200102_1637'),
    ]

    operations = [
        migrations.AlterField(
            model_name='calendar',
            name='categories',
            field=models.ManyToManyField(to='event.Category', verbose_name='Categories'),
        ),
        migrations.AlterField(
            model_name='calendar',
            name='locations',
            field=models.ManyToManyField(to='event.Location', verbose_name='Locations'),
        ),
        migrations.AlterField(
            model_name='category',
            name='slug',
            field=models.SlugField(blank=True, null=True),
        ),
    ]
