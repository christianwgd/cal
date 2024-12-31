import datetime
import json

from django.test import TestCase
from django.contrib import auth
from django.urls import reverse
from django.utils.text import slugify
from django.utils.timezone import now

from event.models import Category, City, Street, Calendar, Event, CONTENT_STATUS_PUBLISHED

User = auth.get_user_model()


class CategoryTestCase(TestCase):

    def setUp(self):
        self.category = Category.objects.create(
            name='test',
            bg_color='#000000',
        )

    def test_category_str(self):
        self.assertEqual(str(self.category), self.category.name)

    def test_category_get_color_bg_dark(self):
        self.category.bg_color = '#999999'
        self.category.save()
        self.category.refresh_from_db()
        color = self.category.get_color()
        self.assertEqual(color.lower(), '#ffffff')

    def test_category_get_color_bg_light(self):
        self.category.bg_color = '#ffffff'
        self.category.save()
        self.category.refresh_from_db()
        color = self.category.get_color()
        self.assertEqual(color.lower(), '#000000')


class CityTests(TestCase):

    def test_city_str(self):
        City.update_cities()
        city = City.objects.get(name='Senden')
        self.assertEqual(str(city), city.name)

    def test_update_cities(self):
        City.update_cities()
        cities = City.objects.all()
        self.assertTrue(cities.count() > 0)
        self.assertEqual(
            cities.get(name='Senden').slug,
            slugify(cities.get(name='Senden').name)
        )

    def test_update_streets(self):
        City.update_cities()
        city = City.objects.get(name='Senden')
        city.update_streets()
        streets = Street.objects.filter(city=city)
        self.assertTrue(streets.count() > 0)
        self.assertEqual(
            streets.filter(name='Wienkamp').first().slug,
            slugify(streets.filter(name='Wienkamp').first().name)
        )


class StreetTests(TestCase):

    def setUp(self):
        City.update_cities()
        self.city = City.objects.get(name='Senden')
        self.city.update_streets()
        self.street = Street.objects.get(name='Wienkamp')

    def test_street_str(self):
        self.assertEqual(str(self.street), f'{self.street.name}, {self.city.name}')

    def test_street_update_categories(self):
        self.street.update_categories()
        categories = Category.objects.all()
        self.assertTrue(categories.count() > 0)
        self.assertEqual(
            categories.get(name='Gelbe Tonne').slug,
            slugify(categories.get(name='Gelbe Tonne').name)
        )


class CalendarTest(TestCase):

    def setUp(self):
        City.update_cities()
        self.city = City.objects.get(name='Senden')
        self.city.update_streets()
        self.street = Street.objects.get(name='Wienkamp')
        self.calendar = Calendar.objects.create(
            street=self.street,
            slug=slugify(self.street),
            city=self.city,
            default=True,
            owner=User.objects.create(username='username')
        )

    def test_calendar_str(self):
        self.assertEqual(str(self.calendar), self.calendar.name)

    def test_calendar_update_events(self):
        self.city.update_streets()
        self.street.update_categories()
        self.calendar.categories.add(Category.objects.get(slug='restmull-4-wo'))
        self.calendar.update_events()
        events = Event.objects.filter(calendar=self.calendar)
        self.assertTrue(events.count() > 0)
        self.assertTrue(events.first().category in self.calendar.categories.all())

    def test_calendar_view(self):
        response = self.client.get(reverse('event:calendar'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('event/event_calendar.html')
        self.assertQuerySetEqual(
            response.context['calendars'],
            Calendar.objects.all(),
        )

    def test_calendar_edit_get(self):
        response = self.client.get(reverse('event:edit', kwargs={'pk': self.calendar.id}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('event/event_edit.html')

    def test_calendar_events_as_json(self):
        category = Category.objects.create(
            name='test',
            bg_color='#000000',
        )
        category.color = category.get_color()
        category.save()
        self.calendar.categories.add(category)
        year = now().year
        month = now().month
        event = Event.objects.create(
            date = datetime.date(year, month, 15),
            calendar=self.calendar,
            category=category,
            state=CONTENT_STATUS_PUBLISHED,
            version=0
        )
        get_params = f'?start={year}-{month}-01&end={year}-{month}-28'
        url = reverse('event:events') + get_params
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        d_resp = json.loads(response.content)
        self.assertEqual(len(d_resp), 1)
        elem = d_resp[0]
        self.assertEqual(elem['title'], '$ICON test\nWienkamp, Senden, Senden')
        self.assertEqual(elem['start'], event.date.strftime('%Y-%m-%d'))
        self.assertEqual(elem['icon'], None)
        self.assertEqual(elem['textColor'], '#ffffff')
        self.assertEqual(elem['backgroundColor'], '#000000')
