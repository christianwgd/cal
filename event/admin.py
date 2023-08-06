from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _

from event.models import Event, Category, Calendar, City, Street


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = ['name']
    search_fields = ['name']


@admin.register(Street)
class StreetAdmin(admin.ModelAdmin):

    @admin.action(description=_("Update categories"))
    def action_update_categories(self, request, queryset=None):
        street = queryset.first()
        street.update_categories()
        messages.success(request, _('Categories updated.'))

    list_display = ['name', 'city']
    list_filter = ['city']
    search_fields = ['name']
    actions = [action_update_categories]


@admin.register(City)
class CityAdmin(admin.ModelAdmin):

    @admin.action(description=_("Update cities"))
    def action_update_cities(self, request, queryset):
        city = queryset.first()
        city.update_cities()
        messages.success(request, _('Cities updated.'))

    @admin.action(description=_("Update streets for selected city"))
    def action_update_streets(self, request, queryset):
        for city in queryset:
            city.update_streets()
        messages.success(request, _('Streets updated.'))

    list_display = ['name', 'slug']
    search_fields = ['name']
    actions = [action_update_cities, action_update_streets]


@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):

    @admin.action(description=_("Update events for selected calendars"))
    def action_update_events(self, request, queryset=None):
        for cal in queryset:
            cal.update_events()
        messages.success(request, _('Events updated.'))

    list_display = ['name', 'slug', 'default']
    autocomplete_fields = ['categories']
    actions = [action_update_events]

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):

    list_display = ['date', 'calendar', 'category']
    list_filter = ['calendar', 'category']
    date_hierarchy = 'date'
