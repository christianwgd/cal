# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import gettext_lazy as _
from colorful.fields import RGBColorField


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

    name = models.CharField(max_length=50, verbose_name=_('Name'))
    bg_color = RGBColorField(verbose_name=_('Background color'),blank=True, null=True)
    color = RGBColorField(verbose_name=_('Color'), blank=True, null=True)
    slug = models.SlugField(blank=True, null=True)


class Location(models.Model):

    class Meta:
        verbose_name = _('Location')
        verbose_name_plural = _('Locations')

    def __str__(self):
        return self.name

    name = models.CharField(max_length=50, verbose_name=_('Name'))
    char = models.CharField(
        max_length=2, verbose_name=_('Character'),
        blank=True, null=True
    )
    slug = models.SlugField(blank=True, null=True)


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

    name = models.CharField(max_length=50, verbose_name=_('Name'))
    categories = models.ManyToManyField(Category, verbose_name=_('Categories'))
    locations = models.ManyToManyField(Location, verbose_name=_('Locations'))
    def_loc = models.ForeignKey(
        Location, verbose_name=_('Default location'),
        on_delete=models.SET_NULL, related_name='default',
        blank=True, null=True
    )
    icon = models.CharField(
        max_length=20, verbose_name=_('Icon'),
        blank=True, null=True
    )
    slug = models.SlugField(blank=True, null=True)
    default = models.BooleanField(default=False, verbose_name=_('Default'))


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
        super(Event, self).save(*args, **kwargs)

    date = models.DateField(
        auto_now_add=False, verbose_name=_('Date')
    )
    calendar = models.ForeignKey(
        Calendar, on_delete=models.PROTECT, verbose_name=_('Calendar')
    )
    category = models.ForeignKey(
        Category, on_delete=models.PROTECT, verbose_name=_('Category')
    )
    location = models.ForeignKey(
        Location, on_delete=models.PROTECT, verbose_name=_('Location'),
        blank=True, null=True
    )
    state = models.IntegerField(
        verbose_name=_('State'),
        choices=CONTENT_STATUS_CHOICES, default=CONTENT_STATUS_PUBLISHED,
        help_text=_("With Draft chosen, will only be shown for admin users on the site.")
    )
    version = models.PositiveSmallIntegerField(
        verbose_name=_('Version'), default=0
    )