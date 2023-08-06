# -*- coding: utf-8 -*-
from datetime import datetime, date

import requests
from django.conf import settings
from django.db import models
from django.contrib import auth
from django.utils.text import slugify
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from colorful.fields import RGBColorField
from smart_selects.db_fields import ChainedForeignKey

User = auth.get_user_model()


CONTENT_STATUS_DRAFT = 1
CONTENT_STATUS_PUBLISHED = 2
CONTENT_STATUS_CHOICES = (
    (CONTENT_STATUS_DRAFT, _('Draft')),
    (CONTENT_STATUS_PUBLISHED, _('Published')),
)


def call_api(url):
    base_url = getattr(settings, 'API_BASE_URL', None)
    if not base_url:
        msg = 'No API_BASE_URL configured!'
        raise ImportError(msg)
    url = base_url + url
    r = requests.get(url, timeout=20)
    if r.status_code == 200:
        return r.json()
    return None


class Category(models.Model):

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')

    def __str__(self):
        return self.name

    def get_color(self):
        color = self.bg_color[1:]

        hex_red = int(color[0:2], base=16)
        hex_green = int(color[2:4], base=16)
        hex_blue = int(color[4:6], base=16)

        luminance = hex_red * 0.3 + hex_green * 0.4 + hex_blue * 0.3
        if luminance < 180:
            return '#ffffff'
        return '#000000'

    def save(self, *args, **kwargs):
        if self.color:
            self.color = self.get_color()
        super().save(*args, **kwargs)

    name = models.CharField(max_length=50, verbose_name=_('Name'))
    bg_color = RGBColorField(verbose_name=_('Background color'),blank=True, null=True)
    color = RGBColorField(verbose_name=_('Color'), blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)


class City(models.Model):

    class Meta:
        verbose_name = _('City')
        verbose_name_plural = _('Cities')
        ordering = ['name']

    def __str__(self):
        return self.name

    name = models.CharField(max_length=50, verbose_name=_('Name'))
    slug = models.SlugField(blank=True, null=True)

    @staticmethod
    def update_cities():
        # https://coe-abfallapp.regioit.de/abfall-app-coe/rest/orte
        cities = call_api('orte')
        for city in cities:
            location, created = City.objects.get_or_create(
                id=city['id'],
                defaults={
                    'name': city['name'],
                    'slug': slugify(city['name']),
                }
            )
            if not created:
                location.name = city['name']
                location.slug = slugify(location.name)
                location.save()

    def update_streets(self):
        # https://coe-abfallapp.regioit.de/abfall-app-coe/rest/orte/1216636/strassen
        streets = call_api(f'orte/{self.id}/strassen')
        for street in streets:
            location, created = Street.objects.get_or_create(
                id=street['id'],
                defaults={
                    'name': street['name'],
                    'slug': slugify(street['name']),
                    'city': self
                }
            )
            if not created:
                location.name = street['name']
                location.slug = slugify(location.name)
                location.city = self
                location.save()


class Street(models.Model):

    class Meta:
        verbose_name = _('Street')
        verbose_name_plural = _('Streets')
        ordering = ['city', 'name']

    def __str__(self):
        return f'{self.name}, {self.city}'

    name = models.CharField(max_length=50, verbose_name=_('Name'))
    slug = models.SlugField(blank=True, null=True)
    city = models.ForeignKey(City, verbose_name=_('City'), on_delete=models.CASCADE)

    @staticmethod
    def update_categories():
        # https://coe-abfallapp.regioit.de/abfall-app-coe/rest/fraktionen
        categories = call_api('fraktionen')
        for cat in categories:
            category, created = Category.objects.get_or_create(
                id=cat['id'],
                defaults={
                    'name': cat['name'],
                    'slug': slugify(cat['name']),
                    'bg_color': f"#{cat['farbeRgb']}"
                }
            )
            if not created:
                category.name = cat['name']
                category.slug = slugify(category.name)
                category.bg_color = f"#{cat['farbeRgb']}"
                category.color = category.get_color()
                category.save()
            else:
                category.color = category.get_color()
                category.save()


class Calendar(models.Model):

    class Meta:
        verbose_name = _('Calendar')
        verbose_name_plural = _('Calendars')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if self.default is True:
            if self.id:
                Calendar.objects.exclude(pk=self.id).update(default=False)
            else:
                Calendar.objects.all().update(default=False)
        super(Calendar, self).save(*args, **kwargs)

    @property
    def name(self):
        return f'{self.city.name}, {self.street.name}'

    categories = models.ManyToManyField(Category, verbose_name=_('Categories'))
    city = models.ForeignKey(City, verbose_name=_('City'), on_delete=models.CASCADE)
    street = ChainedForeignKey(
        Street, verbose_name=_('Street'), on_delete=models.CASCADE,
        chained_field='city', chained_model_field='city',
    )
    icon = models.CharField(
        max_length=20, verbose_name=_('Icon'),
        blank=True, null=True
    )
    slug = models.SlugField(blank=True, null=True)
    default = models.BooleanField(default=False, verbose_name=_('Default'))
    owner = models.ForeignKey(User, verbose_name=_('Owner'), on_delete=models.CASCADE)
    auto_update = models.BooleanField(default=False, verbose_name=_('Auto update calendar'))

    def update_events(self):
        events = call_api(f'strassen/{self.street.id}/termine')
        first_of_year = date(now().year, 1, 1)
        for termin in events:
            if Category.objects.filter(id=termin['bezirk']['fraktionId']).exists():
                category = Category.objects.get(id=termin['bezirk']['fraktionId'])
                if category in self.categories.all():
                    dt = datetime.strptime(termin['datum'], '%Y-%m-%d').date()
                    if dt > first_of_year:
                        event, created = Event.objects.get_or_create(
                            id=termin['id'],
                            defaults={
                                'date': dt,
                                'calendar': self,
                                'category': category,
                                'state': CONTENT_STATUS_PUBLISHED
                            }
                        )
                        if not created:
                            changed = False
                            if event.date != dt:
                                event.date = dt
                                changed = True
                            if event.category != category:
                                event.category = category
                                changed = True
                            if changed:
                                event.version += 1
                                event.save()


class Event(models.Model):

    class Meta:
        verbose_name = _('Event')
        verbose_name_plural = _('Events')

    def __str__(self):
        return '{date}-{vers}: {cal} - {cat}'.format(
            cal = self.calendar,
            cat = self.category,
            date = self.date,
            vers = self.version
        )

    def save(self, *args, **kwargs):
        if self.version:
            self.version += 1
        super().save(*args, **kwargs)

    date = models.DateField(
        auto_now_add=False, verbose_name=_('Date')
    )
    calendar = models.ForeignKey(
        Calendar, on_delete=models.PROTECT, verbose_name=_('Calendar'),
        related_name='events'
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, verbose_name=_('Category')
    )
    state = models.IntegerField(
        verbose_name=_('State'),
        choices=CONTENT_STATUS_CHOICES, default=CONTENT_STATUS_PUBLISHED,
        help_text=_("With Draft chosen, will only be shown for admin users on the site.")
    )
    version = models.PositiveSmallIntegerField(
        verbose_name=_('Version'), default=0
    )
