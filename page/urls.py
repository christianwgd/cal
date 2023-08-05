from django.urls import path

from page import views

app_name = 'page'

urlpatterns = [
    path('<slug:slug>/', views.PageDetailView.as_view(), name='page-view'),
]
