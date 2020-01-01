# -*- coding: utf-8 -*-
import json
import dateutil.parser
from django.utils import formats

from django.http import HttpResponse
from django.views.generic import ListView

from event.models import Event, Location, CONTENT_STATUS_PUBLISHED


class EventListView(ListView):
    model = Event

    def get_context_data(self, **kwargs):
        context = super(EventListView, self).get_context_data(**kwargs)
        context['locations'] = Location.objects.all()
        return context


def events_as_json(request, calendar=None, location=None):

    print(calendar, location)

    start_str = request.GET['start']
    end_str = request.GET['end']
    von = dateutil.parser.parse(start_str)
    bis =  dateutil.parser.parse(end_str)

    cal = []
    if calendar and location:
        events = Event.objects.filter(
            calendar__slug=calendar,
            location__slug=location,
            date__range=(von, bis),
            state=CONTENT_STATUS_PUBLISHED
        ).order_by('date')
    else:
        events = Event.objects.filter(
            date__range=(von, bis),
            state=CONTENT_STATUS_PUBLISHED
        ).order_by('date')
    for event in events:
        cal_item = {
            'title': '$ICON {}'.format(event.location),
            'start': formats.date_format(event.date, 'Y-m-d'),
            'icon': event.calendar.icon,
            'textColor': event.category.color,
            'borderColor': event.category.bg_color,
            'backgroundColor': event.category.bg_color
        }
        cal.append(cal_item)

    return HttpResponse(json.dumps(cal))