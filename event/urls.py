from django.urls import path

from event import views

app_name = 'event'

urlpatterns = [
    path('list/', views.EventListView.as_view(), name='list'),
    path('list/<slug:calendar>/', views.EventListView.as_view(), name='list'),
    path('json/', views.events_as_json, name='as_json'),
    path('json/<slug:calendar>/<slug:location>/', views.events_as_json, name='as_json'),
    path('ical/<slug:cal_slug>/', views.sync_ical, name='as_ical'),
    path('ical/<slug:cal_slug>/<slug:location>/', views.sync_ical, name='as_ical'),
]