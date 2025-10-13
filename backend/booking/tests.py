<<<<<<< HEAD
# LEGACY

# import json
# import datetime as dt
# from .models import Item, Booking
# from ..account.tests.utils import AuthenticatedTestCase

# Create your tests here.

# class BookingTest(AuthenticatedTestCase):
#     def setUp(self):
#         Item.objects.create(name="item1", description="test-item1")
#         Item.objects.create(name="item2", description="test-item2")

#     def testBooking(self):
#         users = [create_admin() for _ in range(5)]

#         Booking.objects.create(item=Item.objects.get(name='item1', description='test-item1'),
#                                start=dt.datetime.now(),end=dt.datetime.now() +\
#                                dt.timedelta(days=1), user=users[0][0])

#         users[0][1].login(username=users[0][0].username, password="Password123")
#         response = users[0][1].get("/booking/bookings/")
#         data = json.loads(response.content.decode('utf-8'))
#         users[0][1].logout()

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(data[0]['item']['name'], 'item1')
#         self.assertEqual(data[0]['user']['username'], users[0][0].username)

#         '''
#         self.client.login(username=self.admin.username, password="Password123")
#         response = self.client.get('/checkin/doorkeepers/', {"user_username":self.admin.username, "event_id":str(meeting.id)})
#         data = json.loads(response.content.decode('utf-8'))
#         self.client.logout()
#         '''
=======
import json
import datetime as dt
from .models import Item, Booking
from ..account.tests.utils import AuthenticatedTestCase

# Create your tests here.

class BookingTest(AuthenticatedTestCase):
    def setUp(self):
        Item.objects.create(name="item1", description="test-item1")
        Item.objects.create(name="item2", description="test-item2")

    def testBooking(self):
        users = [create_admin() for _ in range(5)]

        Booking.objects.create(item=Item.objects.get(name='item1', description='test-item1'),
                               start=dt.datetime.now(),end=dt.datetime.now() +\
                               dt.timedelta(days=1), user=users[0][0])

        users[0][1].login(username=users[0][0].username, password="Password123")
        response = users[0][1].get("/booking/bookings/")
        data = json.loads(response.content.decode('utf-8'))
        users[0][1].logout()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(data[0]['item']['name'], 'item1')
        self.assertEqual(data[0]['user']['username'], users[0][0].username)

        '''
        self.client.login(username=self.admin.username, password="Password123")
        response = self.client.get('/checkin/doorkeepers/', {"user_username":self.admin.username, "event_id":str(meeting.id)})
        data = json.loads(response.content.decode('utf-8'))
        self.client.logout()
        '''
>>>>>>> ebf8241 (fix: rename src folder to backend to better fit python naming standards)
