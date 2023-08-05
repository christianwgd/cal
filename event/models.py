# -*- coding: utf-8 -*-
from django.db import models
from django.contrib import auth
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


class Street(models.Model):

    class Meta:
        verbose_name = _('Street')
        verbose_name_plural = _('Streets')
        ordering = ['city', 'name']

    def __str__(self):
        return f'{self.city}, {self.name}'

    name = models.CharField(max_length=50, verbose_name=_('Name'))
    slug = models.SlugField(blank=True, null=True)
    city = models.ForeignKey(City, verbose_name=_('City'), on_delete=models.CASCADE)


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
