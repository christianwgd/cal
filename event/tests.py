from django.test import TestCase
from django.contrib import auth
from django.utils.text import slugify

from event.models import Category, City, Street, Calendar, Event
from event.views import update_cities, update_streets, update_categories, update_events

User = auth.get_user_model()


class CategoryTestCase(TestCase):

    def setUp(self):
        self.category = Category.objects.create(
            name='test',
            bg_color='#000000',
        )

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


class UpdateTest(TestCase):

    def test_update_location_cities(self):
        update_cities()
        cities = City.objects.all()
        self.assertTrue(cities.count() > 0)
        self.assertEqual(
            cities.get(name='Senden').slug,
            slugify(cities.get(name='Senden').name)
        )

    def test_update_location_streets(self):
        city = City.objects.create(id=1216636, name='Senden')
        update_streets(city)
        streets = Street.objects.all()
        self.assertTrue(streets.count() > 0)
        self.assertEqual(
            streets.get(name='Wienkamp').slug,
            slugify(streets.get(name='Wienkamp').name)
        )

    def test_update_categories(self):
        update_categories()
        categories = Category.objects.all()
        self.assertTrue(categories.count() > 0)
        self.assertEqual(
            categories.get(name='Gelbe Tonne').slug,
            slugify(categories.get(name='Gelbe Tonne').name)
        )

    def test_update_events(self):
        update_categories()
        city = City.objects.create(id=1216636, name='Senden')
        street = Street.objects.create(id=1216830, name='Wienkamp', city=city)
        calendar = Calendar.objects.create(
            name='Kalender',
            street=street,
            default=True,
            owner=User.objects.create(username='username')
        )
        calendar.categories.add(Category.objects.get(id=6))
        update_events(calendar)
        events = Event.objects.all()
        self.assertTrue(events.count() > 0)
        self.assertTrue(events.first().category in calendar.categories.all())
