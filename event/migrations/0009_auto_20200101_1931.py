# Generated by Django 3.0.1 on 2020-01-01 18:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('event', '0008_category_bg_color'),
    ]

    operations = [
        migrations.RenameField(
            model_name='event',
            old_name='status',
            new_name='state',
        ),
    ]
