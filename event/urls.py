from django.urls import path

from event import views

app_name = 'event'

urlpatterns = [
    path('calendar/', views.EventCalendarView.as_view(), name='calendar'),
    path('calendar/<slug:calendar>/', views.EventCalendarView.as_view(), name='calendar'),
    path('calendar/<slug:calendar>/<slug:location>/', views.EventCalendarView.as_view(), name='calendar'),

    path('edit/<int:pk>/', views.CalendarEdit.as_view(), name='edit'),

    path('events/', views.events_as_json, name='events'),
    path('events/<slug:calendar>/<slug:location>/', views.events_as_json, name='events'),

    path('list/<slug:calendar>/<slug:location>/<slug:category>/', views.event_list, name='list'),

    path('ical/<slug:cal_slug>/', views.sync_ical, name='as_ical'),
    path('ical/<slug:cal_slug>/<slug:location>/', views.sync_ical, name='as_ical'),
    path('ical/<slug:cal_slug>/<slug:location>/<int:alarm_time>/', views.sync_ical, name='as_ical'),

    path('loc_options/<slug:cal_slug>/', views.get_location_options),
    path('cat_options/<slug:cal_slug>/', views.get_category_options),

    path('create/<slug:cal_slug>/<slug:loc_slug>/<slug:cat_slug>/<str:dat_str>/', views.create_event),
    path('delete/<int:event_id>/', views.delete_event),
    path('update/<int:pk>/', views.EventUpdateView.as_view(), name='update'),
]