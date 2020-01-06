# Generated by Django 3.0.2 on 2020-01-06 19:38

import ckeditor_uploader.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, db_index=True)),
                ('title', models.CharField(max_length=200, verbose_name='Title')),
                ('slug', models.SlugField(max_length=200)),
                ('status', models.IntegerField(choices=[(1, 'Draft'), (2, 'Published')], default=2, help_text='With Draft chosen, will only be shown for admin users on the site.', verbose_name='Status')),
                ('name', models.CharField(max_length=50, verbose_name='name')),
                ('icon', models.CharField(blank=True, max_length=20, null=True, verbose_name='icon')),
                ('content', ckeditor_uploader.fields.RichTextUploadingField(blank=True, null=True, verbose_name='Content')),
                ('menu', models.IntegerField(choices=[(0, 'None'), (1, 'Header menu'), (2, 'Footer menu')], default=0, verbose_name='menu')),
            ],
            options={
                'verbose_name': 'Page',
                'verbose_name_plural': 'Pages',
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
    ]