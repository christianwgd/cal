# -*- coding: utf-8 -*-
from bootstrap_datepicker_plus import DatePickerInput
from bootstrap_modal_forms.forms import BSModalModelForm
from django.conf import settings
from django.forms import ModelForm
from django.utils.text import slugify

from event.models import Category, Location, Calendar, Event

lang = getattr(settings, "LANGUAGE_CODE", 'de')

class CategoryAdminForm(ModelForm):

    class Meta:
        model = Category
        fields = '__all__'

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        name = self.cleaned_data['name']
        if not slug:
            slug = slugify(name)
        return slug


class LocationAdminForm(ModelForm):

    class Meta:
        model = Location
        fields = '__all__'

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        name = self.cleaned_data['name']
        if not slug:
            slug = slugify(name)
        return slug


class CalendarAdminForm(ModelForm):

    class Meta:
        model = Calendar
        fields = '__all__'

    def clean_slug(self):
        slug = self.cleaned_data['slug']
        name = self.cleaned_data['name']
        print(slug, name)
        if not slug:
            print('modify slug')
            slug = slugify(name)
        print(slug, name)
        return slug


class EventAdminForm(ModelForm):

    class Meta:
        models = Event
        exclude = ['version']

    def __init__(self, *args, **kwargs):
        super(EventAdminForm, self).__init__(*args, **kwargs)
        if 'calendar' in self.initial:
            cal = Calendar.objects.get(pk=self.initial['calendar'])
            self.fields['location'].queryset = cal.locations.all()
            self.fields['category'].queryset = cal.categories.all()


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
            self.fields['location'].choices = (
                    [('','---------')] + [(l.slug, l.name) for l in calendar.locations.all()]
            )
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