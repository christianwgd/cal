# -*- coding: utf-8 -*-
from django.views.generic import ListView

from event.models import Event


class EventListView(ListView):
    model = Event