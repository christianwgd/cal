# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.utils.text import slugify

from ckeditor_uploader.fields import RichTextUploadingField
from orderable.models import Orderable


from page.managers import PagePublishedManager

CONTENT_STATUS_DRAFT = 1
CONTENT_STATUS_PUBLISHED = 2
CONTENT_STATUS_CHOICES = (
    (CONTENT_STATUS_DRAFT, _("Draft")),
    (CONTENT_STATUS_PUBLISHED, _("Published")),
)

MENU_NONE = 0
MENU_TOP = 1
MENU_BOTTOM = 2
MENU_POSITION_CHOICES = (
    (MENU_NONE, _('None')),
    (MENU_TOP, _('Header menu')),
    (MENU_BOTTOM, _('Footer menu')),
)

class Page(Orderable):
    """
    A html page.
    """

    class Meta(Orderable.Meta):
        verbose_name = _("Page")
        verbose_name_plural = _("Pages")

    name = models.CharField(max_length=50, verbose_name=_('name'))
    slug = models.SlugField(max_length=200)
    title = models.CharField(max_length=200, verbose_name=_("title"))
    icon = models.CharField(max_length=20, verbose_name=_("icon"), 
        null=True, blank=True)
    content = RichTextUploadingField(verbose_name=_("Content"), null=True, blank=True)

    status = models.IntegerField(_("Status"),
        choices=CONTENT_STATUS_CHOICES, default=CONTENT_STATUS_PUBLISHED,
        help_text=_("With Draft chosen, will only be shown for admin users "
            "on the site."))
    menu = models.IntegerField(_("menu"), default=MENU_NONE,
        choices=MENU_POSITION_CHOICES)


    objects = PagePublishedManager()

    def __str__(self):
        return self.title

    def published(self):
        """
        For non-staff users, return True when status is published.
        """
        return (self.status == CONTENT_STATUS_PUBLISHED)

    def get_absolute_url(self):
        return reverse('page:page-view', args=[str(self.slug)])

    def save(self, *args, **kwargs):
        if self.title:
            self.slug = slugify(self.name)
        super(Page, self).save(*args, **kwargs)
