from django.urls import path

from event import views

app_name = 'event'

urlpatterns = [
    path('list/', views.EventListView.as_view(), name='list'),
    path('json/', views.events_as_json, name='as_json'),
    path('json/<str:calendar>/<str:location>/', views.events_as_json, name='as_json'),
    path('ical/<str:cal_slug>/', views.sync_ical, name='as_ical'),
    path('ical/<str:cal_slug>/<str:location>/', views.sync_ical, name='as_ical'),
]