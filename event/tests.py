from django.test import TestCase
from django.contrib import auth
from django.utils.text import slugify

from event.models import Category, City, Street, Calendar, Event

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

    def setUp(self):
        self.city = City.objects.create(
            id=1216636,
            name='Senden',
            slug='senden',
        )

    def test_city_str(self):
        self.assertEqual(str(self.city), self.city.name)

    def test_update_cities(self):
        self.city.update_cities()
        cities = City.objects.all()
        self.assertTrue(cities.count() > 0)
        self.assertEqual(
            cities.get(name='Senden').slug,
            slugify(cities.get(name='Senden').name)
        )

    def test_update_streets(self):
        self.city.update_streets()
        streets = Street.objects.filter(city=self.city)
        self.assertTrue(streets.count() > 0)
        self.assertEqual(
            streets.get(name='Wienkamp').slug,
            slugify(streets.get(name='Wienkamp').name)
        )


class StreetTests(TestCase):

    def setUp(self):
        self.city = City.objects.create(
            id=1216636,
            name='Senden',
            slug='senden',
        )
        self.street = Street.objects.create(
            id=1216830,
            name='Wienkamp',
            slug='windkamp',
            city=self.city,
        )

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
        self.city = City.objects.create(id=1216636, name='Senden')
        self.street = Street.objects.create(id=1216830, name='Wienkamp', city=self.city)
        self.calendar = Calendar.objects.create(
            street=self.street,
            city=self.city,
            default=True,
            owner=User.objects.create(username='username')
        )

    def test_calendar_str(self):
        self.assertEqual(str(self.calendar), self.calendar.name)

    def test_calendar_update_events(self):
        self.street.update_categories()
        self.calendar.categories.add(Category.objects.get(id=6))
        self.calendar.update_events()
        events = Event.objects.filter(calendar=self.calendar)
        self.assertTrue(events.count() > 0)
        self.assertTrue(events.first().category in self.calendar.categories.all())
