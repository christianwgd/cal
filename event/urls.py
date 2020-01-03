from django.urls import path

from event import views

app_name = 'event'

urlpatterns = [
    path('calendar/', views.EventCalendarView.as_view(), name='calendar'),
    path('calendar/<slug:calendar>/', views.EventCalendarView.as_view(), name='calendar'),

    path('edit/', views.event_edit, name='edit'),

    path('events/', views.events_as_json, name='events'),
    path('events/<slug:calendar>/<slug:location>/', views.events_as_json, name='events'),

    path('ical/<slug:cal_slug>/', views.sync_ical, name='as_ical'),
    path('ical/<slug:cal_slug>/<slug:location>/', views.sync_ical, name='as_ical'),
]