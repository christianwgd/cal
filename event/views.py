# -*- coding: utf-8 -*-
import json
import dateutil.parser
import datetime
from django.utils import formats

from django.http import HttpResponse
from django.views.generic import ListView
from icalendar import Alarm, vText
from icalendar import Calendar as iCalendar
from icalendar import Event as icalEvent

from event.models import Event, Calendar, CONTENT_STATUS_PUBLISHED


class EventListView(ListView):
    model = Event

    def get_context_data(self, **kwargs):
        context = super(EventListView, self).get_context_data(**kwargs)
        if 'calendar' in self.kwargs:
            context['calendar'] = Calendar.objects.get(
                slug=self.kwargs['calendar']
            )
        else:
            try:
                context['calendar'] = Calendar.objects.get(
                    default=True
                )
            except:
                context['calendar'] = Calendar.objects.first()
        context['locations'] = context['calendar'].locations.all()
        return context


def events_as_json(request, calendar=None, location=None):

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


def sync_ical(request, cal_slug, location=None):

    calendar = Calendar.objects.get(slug=cal_slug)

    now = datetime.datetime.now()
    if location:
        events = Event.objects.filter(
            calendar=calendar,
            location__slug=location,
            date__gte=now,
            state=CONTENT_STATUS_PUBLISHED
        ).order_by('date')
    else:
        events = Event.objects.filter(
            calendar__slug=calendar,
            date__gte=now,
            state=CONTENT_STATUS_PUBLISHED
        ).order_by('date')

    ical = iCalendar()
    ical.add('version', '2.0')
    ical.add('prodid', '-//%s//NONSGML Event Calendar//EN' % calendar.slug.upper())
    ical.add('X-WR-CALNAME', calendar.name)
    ical.add('X-WR-TIMEZONE', 'Europe/Berlin')
    ical.add('method', 'PUBLISH')

    for event in events:
        cal_event = icalEvent()
        cal_event.add('uid', '%s-SNDN-0000-0000-%012d' % (calendar.slug.upper(), event.id))
        cal_event.add('created', now)
        cal_event.add('dtstart', event.date)

        cal_event.add('summary', event.category.name)

        cal_event.add('location', event.location.name)

        cal_event.add('dtstamp', now)
        cal_event.add('sequence', '%d' % event.version)

        alarm = Alarm()
        alarm.add('trigger', vText('-PT16H'))
        alarm.add('action', 'DISPLAY')
        alarm.add('description', '{calname}: {catname}'.format(
            calname = event.calendar.name,
            catname = event.category.name
        ))
        cal_event.add_component(alarm)

        ical.add_component(cal_event)
    # end for

    response = HttpResponse(ical.to_ical(), content_type="text/calendar, text/x-vcalendar, application/hbs-vcs")
    response['Content-Disposition'] = 'attachment; filename="{}.ics"'.format(calendar.slug)
    return response