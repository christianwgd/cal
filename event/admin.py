from django.contrib import admin

from event.models import Event, Category, Calendar, Location


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = ['name',]
    exclude = ['slug',]
    search_fields = ['name']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):

    list_display = ['name',]
    exclude = ['slug',]


@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):

    list_display = ['name',]
    exclude = ['slug', ]
    autocomplete_fields = ['categories']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):

    list_display = ['date', 'calendar', 'category']
    exclude = ['version', ]
