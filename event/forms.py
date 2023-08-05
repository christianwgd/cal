# -*- coding: utf-8 -*-
from bootstrap_datepicker_plus.widgets import DatePickerInput
from bootstrap_modal_forms.forms import BSModalModelForm
from django.conf import settings
from django.forms import ModelForm

from event.models import Event

lang = getattr(settings, "LANGUAGE_CODE", 'de')


class EventForm(ModelForm):

    class Meta:
        model = Event
        exclude = ['version', 'state', 'calendar']
        widgets = {
            'date': DatePickerInput(options={
                "format": "DD.MM.YYYY",
                "locale": lang
            }),
        }

    def __init__(self, *args, **kwargs):
        calendar = kwargs.pop('calendar', None)
        super(EventForm, self).__init__(*args, **kwargs)
        if calendar is not None:
            self.fields['category'].choices = (
                    [('', '---------')] + [(l.slug, l.name) for l in calendar.categories.all()]
            )


class EventUpdateForm(BSModalModelForm):
    class Meta:
        model = Event
        exclude = ['version', 'state', 'calendar']
        widgets = {
            'date': DatePickerInput(options={
                "format": "DD.MM.YYYY",
                "locale": lang
            }),
        }
