"""garbage URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.utils.translation import gettext_lazy as _
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

# Admin Site Config
admin.sites.AdminSite.site_header = _('Calendar')
admin.sites.AdminSite.site_title = _('Calendar')
admin.sites.AdminSite.index_title = 'Index'


urlpatterns = [
    path('admin/', admin.site.urls),

    path('favicon.ico', RedirectView.as_view(url='/static/icons/favicon.ico')),
    path('', RedirectView.as_view(url='/event/calendar/'), name='home'),

    path('event/', include('event.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
