from django.contrib import admin

from event.forms import CategoryAdminForm, LocationAdminForm, CalendarAdminForm, EventAdminForm
from event.models import Event, Category, Calendar, Location


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = ['name', 'slug']
    search_fields = ['name']
    form = CategoryAdminForm


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):

    list_display = ['name', 'slug']
    search_fields = ['name']
    form = LocationAdminForm


@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):

    list_display = ['name', 'slug', 'default']
    autocomplete_fields = ['categories', 'locations']
    form = CalendarAdminForm


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):

    list_display = ['date', 'calendar', 'category']
    list_filter = ['calendar', 'location', 'category']
    form = EventAdminForm
