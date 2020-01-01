from django.urls import path

from event import views

app_name = 'event'

urlpatterns = [
    path('list/', views.EventListView.as_view(), name='list'),
    path('json/', views.events_as_json, name='as_json'),
]