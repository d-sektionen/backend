import json
from django.test import TestCase

import datetime as dt
from .models import Item, Booking
from .admin import BookingAdmin, ItemAdmin
from account.tests import AuthenticatedTestCase, create_admin, create_user
from django.contrib.auth.models import User
from django.test import TestCase

# Create your tests here.

class BookingTest(AuthenticatedTestCase):
    def setUp(self):
        Item.objects.create(name="item1", description="test-item1")
        Item.objects.create(name="item2", description="test-item2")

        
    def testItems(self):
        item1 = Item.objects.get(name="item1")
        item2 = Item.objects.get(name="item2")

        self.assertTrue(item1.description, "test-item1")
        self.assertTrue(item2.description, "test-item2")

    def testBooking(self):
        item1 = Item.objects.get(name="item1")

        admin, client = create_admin()

        Booking.objects.create(item=item1,start=dt.datetime.now(),end=dt.datetime.now() +\
                               dt.timedelta(days=1), user=admin)
        booking = Booking.objects.get(item=item1)

#    def testTodoComeUpWithAName(self):
#        users = [create_admin() for _ in range(5)]
#        for identifier, (user, client) in users.items():
#            print("identifier: " + identifier)
#            print("user, client tuple: " + (user, client))




        
