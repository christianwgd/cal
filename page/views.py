from django.views.generic.detail import DetailView

from page.models import Page


class PageDetailView(DetailView):
    model = Page
