from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin

from page.models import Page


@admin.register(Page)
class PageAdmin(SortableAdminMixin, admin.ModelAdmin):

    list_display = ['title', 'status', 'menu']
    exclude = ['slug']
