from django.contrib import admin

from orderable.admin import OrderableAdmin

from page.models import Page

@admin.register(Page)
class PageAdmin(OrderableAdmin):
    
    list_display = ['title', 'status', 'menu', 'sort_order_display']
    exclude = ('slug', 'sort_order')
