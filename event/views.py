import json
import datetime

from dateutil import parser, relativedelta

from bootstrap_modal_forms.generic import BSModalUpdateView
from django.urls import reverse
from django.utils import formats
from django.http import HttpResponse, JsonResponse
from django.utils import timezone
from django.views.generic import ListView, UpdateView
from django.utils.translation import gettext_lazy as _

from icalendar import Alarm, vText
from icalendar import Calendar as iCalendar
from icalendar import Event as icalEvent

from event.forms import EventUpdateForm, EventForm
from event.models import (
    Event, Calendar, Category,
    CONTENT_STATUS_PUBLISHED
)


class EventCalendarView(ListView):
    model = Event
    template_name = 'event/event_calendar.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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
        form_kwargs = super().get_form_kwargs()
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
            'title': f'$ICON {event.category.name}\n{event.calendar.street}, {event.calendar.street.city}',
            'start': formats.date_format(event.date, 'Y-m-d'),
            'icon': event.calendar.icon,
            'textColor': event.category.color,
            'borderColor': event.category.bg_color,
            'backgroundColor': event.category.bg_color
        }
        cal.append(cal_item)

    return HttpResponse(json.dumps(cal))


def sync_ical(request, cal_slug, alarm_time=None):

    calendar = Calendar.objects.get(slug=cal_slug)

    now = timezone.now() - relativedelta.relativedelta(weeks=1)
    events = Event.objects.filter(
        calendar=calendar,
        date__gte=now,
        state=CONTENT_STATUS_PUBLISHED
    ).order_by('date')

    if alarm_time is None:
        alarm_time = 16

    cal_name = _('Garbage collection')
    ical = iCalendar()
    ical.add('version', '2.0')
    ical.add('prodid', f'-//{calendar.slug.upper()}//NONSGML Event Calendar//EN')
    ical.add('X-WR-CALNAME', f'{cal_name} {calendar.name}')
    ical.add('X-WR-TIMEZONE', 'Europe/Berlin')
    ical.add('method', 'PUBLISH')

    for event in events:
        cal_event = icalEvent()
        cal_event.add('uid', f'{calendar.slug.upper()}-SNDN-0000-0000-{str(event.id).zfill(12)}')
        cal_event.add('created', now)
        cal_event.add('dtstart', event.date)

        cal_event.add('summary', event.category.name)

        cal_event.add('location', event.calendar.street)

        cal_event.add('dtstamp', now)
        cal_event.add('sequence', f'{event.version:d}')

        alarm = Alarm()
        alarm.add('trigger', vText(f'-PT{alarm_time}H'))
        alarm.add('action', 'DISPLAY')
        alarm.add('description', f'{event.calendar.name}: {event.category.name}')
        cal_event.add_component(alarm)

        ical.add_component(cal_event)
    # end for

    response = HttpResponse(ical.to_ical(), content_type="text/calendar, text/x-vcalendar, application/hbs-vcs")
    response['Content-Disposition'] = f'attachment; filename="{calendar.slug}.ics"'
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
    date = datetime.datetime.strptime(dat_str, '%Y-%m-%d')
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
