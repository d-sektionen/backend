import json
import datetime as dt

from django.utils import timezone
from django.test import TestCase
from django.urls import reverse

from account.tests import create_user
from booking.models import Booking, Item

# Create your tests here.
class LogTestCase(TestCase):
    def setUp(self):
        self.user, self.client = create_user()
        self.start_url = reverse('starts-list')
        self.entry_url = reverse('entries-list')
        
        self.valid_start_data = {
            'booking_liu_id': self.user.username,
            'start_km': 42069,
            'start_message': 'this is a start message',
            'start_car_cleaned': False
        }
        self.invalid_start_data = {
            'booking_liu_id': 'self.user.username',
            'start_km': '42069',
            'start_message': 123,
            'start_car_cleaned': 'false'
        }

        self.valid_entry_data = {
            'booking_liu_id': self.user.username,
            'end_km': 42070,
            'end_message': 'this is an end message',
            'end_car_cleaned': True,
            'car_days': 1,
            'trailer_days': 1,
            'trailer': False
        }
        self.invalid_entry_data = {
            'booking_liu_id': 'self.user.username',
            'end_km': '42070',
            'end_message': 32,
            'end_car_cleaned': 'true',
            'car_days': '1',
            'trailer_days': '1',
            'trailer': 'false'
        }

        self.client.login(username=self.user.username, password='Password123')
        token_response = self.client.get('/account/token/')
        token_data = json.loads(token_response.content.decode('utf-8'))
        self.client.credentials(HTTP_AUTHORIZATION='JWT ' + token_data['access'])
        # self.client.logout()

        Item.objects.create(name="Kianu Revs", description="kianu-revs-1")
        Booking.objects.create(item=Item.objects.get(name='Kianu Revs', description='kianu-revs-1'),
                               start=dt.datetime.now(tz=timezone.utc),end=dt.datetime.now(tz=timezone.utc) +\
                               dt.timedelta(days=1), user=self.user)

    def test_create_valid_start(self):
        resp = self.client.post(self.start_url, json.dumps(self.valid_start_data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)

    def test_create_valid_entry(self):
        self.test_create_valid_start()
        resp = self.client.post(self.entry_url, json.dumps(self.valid_entry_data), content_type='application/json')
        self.assertEqual(resp.status_code, 200)

    def test_create_invalid_start(self):
        # Test invalid data types
        for key in self.valid_start_data:
            data_copy = self.valid_start_data.copy()
            data_copy[key] = self.invalid_start_data[key]
            resp = self.client.post(self.start_url, json.dumps(data_copy), content_type='application/json')

            if key == 'booking_liu_id':
                self.assertEqual(resp.status_code, 404)
            else:
                self.assertEqual(resp.status_code, 400)

        # Test missing data
        for key in self.valid_start_data:
            data_copy = self.valid_start_data.copy()
            data_copy.pop(key)
            resp = self.client.post(self.start_url, json.dumps(data_copy), content_type='application/json')
            self.assertEqual(resp.status_code, 400)

    def test_create_invalid_entry(self):
        # Test creating when there is no start log
        resp = self.client.post(self.entry_url, json.dumps(self.valid_entry_data), content_type='application/json')
        self.assertEqual(resp.status_code, 404)
        self.test_create_valid_start()

        # Test invalid data types
        for key in self.valid_entry_data:
            data_copy = self.valid_entry_data.copy()
            data_copy[key] = self.invalid_entry_data[key]
            resp = self.client.post(self.entry_url, json.dumps(data_copy), content_type='application/json')

            if key == 'booking_liu_id':
                self.assertEqual(resp.status_code, 404)
            else:
                self.assertEqual(resp.status_code, 400)

        # Test missing data
        for key in self.valid_entry_data:
            data_copy = self.valid_entry_data.copy()
            data_copy.pop(key)
            resp = self.client.post(self.entry_url, json.dumps(data_copy), content_type='application/json')
            self.assertEqual(resp.status_code, 400)

        # Test invalid data values
        for key in self.valid_entry_data:
            data_copy = self.valid_entry_data.copy()
            if key == 'car_days' or key == 'trailer_days':
                data_copy[key] = 0
                resp = self.client.post(self.entry_url, json.dumps(data_copy), content_type='application/json')
                self.assertEqual(resp.status_code, 400)