# -*- coding: utf-8 -*-
import json
import dateutil.parser
import datetime

from django.shortcuts import render
from django.utils import formats
from django.http import HttpResponse, JsonResponse
from django.views.generic import ListView

from icalendar import Alarm, vText
from icalendar import Calendar as iCalendar
from icalendar import Event as icalEvent

from event.models import (
    Event, Calendar, Location, Category,
    CONTENT_STATUS_PUBLISHED
)


class EventCalendarView(ListView):
    model = Event
    template_name = 'event/event_calendar.html'

    def get_context_data(self, **kwargs):
        context = super(EventCalendarView, self).get_context_data(**kwargs)
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
        if 'location' in self.kwargs:
            context['def_loc'] = self.kwargs['location']
        return context


def event_edit(request):
    calendars = Calendar.objects.all()
    return render(request, 'event/event_edit.html', {'calendars': calendars})


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


def event_list(request, calendar, location, category):

    events = Event.objects.filter(
        calendar__slug=calendar,
        location__slug=location,
        category__slug=category
    ).order_by('-date')

    jsnEvents = []
    for event in events:
        jsnEvent = {
            'id': event.id,
            'date': formats.date_format(event.date, "SHORT_DATE_FORMAT"),
            'calendar': event.calendar.name,
            'location': event.location.name,
            'category': event.category.name
        }
        jsnEvents.append(jsnEvent)

    return JsonResponse(jsnEvents, safe=False)


def get_location_options(request, cal_slug):

    calendar = Calendar.objects.get(slug=cal_slug)
    loc_options = []
    for location in calendar.locations.all():
        loc_options.append({
            'value': location.slug,
            'name': location.name
        })

    return JsonResponse(loc_options, safe=False)


def get_category_options(request, cal_slug):

    calendar = Calendar.objects.get(slug=cal_slug)
    cat_options = []
    for category in calendar.categories.all():
        cat_options.append({
            'value': category.slug,
            'name': category.name
        })

    return JsonResponse(cat_options, safe=False)


def create_event(request, cal_slug, loc_slug, cat_slug, dat_str):
    date = datetime.datetime.strptime(dat_str, '%d.%m.%Y')
    calendar = Calendar.objects.get(slug=cal_slug)
    location = Location.objects.get(slug=loc_slug)
    category = Category.objects.get(slug=cat_slug)
    Event.objects.create(
        date=date,
        calendar=calendar,
        location=location,
        category=category,
        state=CONTENT_STATUS_PUBLISHED
    )
    return JsonResponse('', safe=False)


def delete_event(request, event_id):
    Event.objects.get(pk=event_id).delete()
    return JsonResponse('Deleted', safe=False)