# -*- coding: utf-8 -*-
from orderable.managers import OrderableManager
from django.utils.translation import gettext_lazy as _


class PagePublishedManager(OrderableManager):
    """
    For non-staff users, return items with a published status.
    """

    def published(self, for_user=None):
        from page.models import CONTENT_STATUS_PUBLISHED
        if for_user is not None and for_user.is_staff:
            return self.all()
        return self.filter(status=CONTENT_STATUS_PUBLISHED)

    def get_by_natural_key(self, slug):
        return self.get(slug=slug)
