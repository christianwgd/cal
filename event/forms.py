# -*- coding: utf-8 -*-
from bootstrap_modal_forms.forms import BSModalModelForm
from django.forms import ModelForm, DateInput

from event.models import Event


class EventForm(ModelForm):

    class Meta:
        model = Event
        exclude = ['version', 'state', 'calendar']
        widgets = {
            'date': DateInput(attrs={'type': 'date'},),
        }

    def __init__(self, *args, **kwargs):
        calendar = kwargs.pop('calendar', None)
        super(EventForm, self).__init__(*args, **kwargs)
        if calendar is not None:
            self.fields['category'].choices = (
                [('', '---------')] + [(cat.slug, cat.name) for cat in calendar.categories.all()]
            )


class EventUpdateForm(BSModalModelForm):
    class Meta:
        model = Event
        exclude = ['version', 'state', 'calendar']
        widgets = {
            'date': DateInput(attrs={'type': 'date'},),
        }
