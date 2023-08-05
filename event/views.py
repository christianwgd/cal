# -*- coding: utf-8 -*-
import json
import datetime

import requests
from dateutil import parser, relativedelta

from bootstrap_modal_forms.generic import BSModalUpdateView
from django.conf import settings
from django.urls import reverse
from django.utils import formats
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.timezone import now
from django.views.generic import ListView, UpdateView
from django.utils.translation import gettext_lazy as _

from icalendar import Alarm, vText
from icalendar import Calendar as iCalendar
from icalendar import Event as icalEvent

from event.forms import EventUpdateForm, EventForm
from event.models import (
    Event, Calendar, Category,
    CONTENT_STATUS_PUBLISHED, Street, City
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
            except Calendar.DoesNotExist:
                context['calendar'] = Calendar.objects.first()
        context['calendars'] = Calendar.objects.all()
        return context


class CalendarEdit(UpdateView):
    model = Calendar
    form_class = EventForm
    template_name = 'event/event_edit.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['calendars'] = Calendar.objects.all()
        return ctx

    def get_initial(self):
        initial = super().get_initial()
        initial['location'] = self.request.GET.get('location', None)
        initial['category'] = self.request.GET.get('category', None)
        initial['date'] = timezone.now()
        return initial

    def get_form_kwargs(self, *args, **kwargs):
        form_kwargs = super(CalendarEdit, self).get_form_kwargs()
        form_kwargs['calendar'] = self.object
        return form_kwargs


def events_as_json(request, calendar=None):
    start_str = request.GET['start']
    end_str = request.GET['end']
    von = parser.parse(start_str)
    bis =  parser.parse(end_str)

    cal = []
    if calendar:
        events = Event.objects.filter(
            calendar__slug=calendar,
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
            'title': '$ICON {}\n{}, {}'.format(
                event.category.name, event.calendar.street, event.calendar.street.city
            ),
            'start': formats.date_format(event.date, 'Y-m-d'),
            'icon': event.calendar.icon,
            'textColor': event.category.color,
            'borderColor': event.category.bg_color,
            'backgroundColor': event.category.bg_color
        }
        cal.append(cal_item)

    return HttpResponse(json.dumps(cal))


def sync_ical(request, cal_slug, location=None, alarm_time=None):

    calendar = Calendar.objects.get(slug=cal_slug)

    now = timezone.now() - relativedelta.relativedelta(weeks=1)
    events = Event.objects.filter(
        calendar=calendar,
        date__gte=now,
        state=CONTENT_STATUS_PUBLISHED
    ).order_by('date')

    if alarm_time is None:
        alarm_time = 16

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
        alarm.add('trigger', vText('-PT{}H'.format(alarm_time)))
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


def event_list(request, calendar, category):

    events = Event.objects.filter(
        calendar__slug=calendar,
        category__slug=category,
        date__gte=timezone.now()
    ).order_by('date')

    jsn_events = []
    for event in events:
        jsn_event = {
            'id': event.id,
            'date': formats.date_format(event.date, "SHORT_DATE_FORMAT"),
            'calendar': event.calendar.name,
            'category': event.category.name
        }
        jsn_events.append(jsn_event)

    return JsonResponse(jsn_events, safe=False)


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


def create_event(request, cal_slug, cat_slug, dat_str):
    date = datetime.datetime.strptime(dat_str, '%d.%m.%Y')
    calendar = Calendar.objects.get(slug=cal_slug)
    category = Category.objects.get(slug=cat_slug)
    Event.objects.create(
        date=date,
        calendar=calendar,
        category=category,
        state=CONTENT_STATUS_PUBLISHED
    )
    return JsonResponse('', safe=False)


def delete_event(request, event_id):
    Event.objects.get(pk=event_id).delete()
    return JsonResponse('Deleted', safe=False)


class EventUpdateView(BSModalUpdateView):
    model = Event
    form_class = EventUpdateForm
    success_message = _('Event updated')

    def get_success_url(self):
        form = self.get_form()
        cat = Category.objects.get(pk=form.data['category'])
        return '{url}?category={cat}'.format(
            url=reverse('event:edit', kwargs={ 'pk': self.object.calendar.id }),
            cat=cat.slug,
        )


def call_api(url):
    base_url = getattr(settings, 'API_BASE_URL', None)
    if not base_url:
        msg = 'No API_BASE_URL configured!'
        raise ImportError(msg)
    url = base_url + url
    r = requests.get(url, timeout=20)
    if r.status_code == 200:
        return r.json()
    return None


def update_cities():
    # https://coe-abfallapp.regioit.de/abfall-app-coe/rest/orte
    cities = call_api('orte')
    for city in cities:
        location, created = City.objects.get_or_create(
            id=city['id'],
            defaults={
                'name': city['name'],
                'slug': slugify(city['name']),
            }
        )
        if not created:
            location.name = city['name']
            location.slug = slugify(location.name)
            location.save()

def update_streets(city):
    # https://coe-abfallapp.regioit.de/abfall-app-coe/rest/orte/1216636/strassen
    streets = call_api(f'orte/{city.id}/strassen')
    for street in streets:
        location, created = Street.objects.get_or_create(
            id=street['id'],
            defaults={
                'name': street['name'],
                'slug': slugify(street['name']),
                'city': city
            }
        )
        if not created:
            location.name = street['name']
            location.slug = slugify(location.name)
            location.city = city
            location.save()


def update_categories():
    # https://coe-abfallapp.regioit.de/abfall-app-coe/rest/fraktionen
    categories = call_api('fraktionen')
    for cat in categories:
        category, created = Category.objects.get_or_create(
            id=cat['id'],
            defaults={
                'name': cat['name'],
                'slug': slugify(cat['name']),
                'bg_color': f"#{cat['farbeRgb']}"
            }
        )
        if not created:
            category.name = cat['name']
            category.slug = slugify(category.name)
            category.bg_color = f"#{cat['farbeRgb']}"
            category.color = category.get_color()
            category.save()


def update_events(calendar):
    events = call_api(f'strassen/{calendar.street.id}/termine')
    for termin in events:
        if Category.objects.filter(id=termin['bezirk']['fraktionId']).exists():
            category = Category.objects.get(id=termin['bezirk']['fraktionId'])
            if category in calendar.categories.all():
                date = datetime.datetime.strptime(termin['datum'], '%Y-%m-%d')
                if date.date() > now().date():
                    event, created = Event.objects.get_or_create(
                        id=termin['id'],
                        defaults={
                            'date': date,
                            'calendar': calendar,
                            'category': category,
                            'state': CONTENT_STATUS_PUBLISHED
                        }
                    )
                    if not created:
                        changed = False
                        if event.date != date:
                            event.date = date
                            changed = True
                        if event.category != category:
                            event.category = category
                            changed = True
                        if changed:
                            event.version += 1
                            event.save()
