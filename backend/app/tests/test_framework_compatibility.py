from io import BytesIO
from tempfile import TemporaryDirectory
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.utils import timezone
from icalendar import Calendar
from PIL import Image

from backend.account.feeds import CalendarFeed
from backend.account.models import CalendarSubscription
from backend.booking.models import Booking, ItemPool
from backend.voting.serializers import PublicAlternativeSerializer


class FrameworkCompatibilityTests(SimpleTestCase):
    def test_nested_list_validation_keeps_positional_errors(self):
        serializer = PublicAlternativeSerializer(
            data=[{"text": "Valid option"}, {"text": ""}], many=True
        )
        self.assertFalse(serializer.is_valid())
        self.assertIsInstance(serializer.errors, list)
        self.assertEqual(serializer.errors[0], {})
        self.assertEqual(serializer.errors[1]["text"][0].code, "blank")

    def test_imagekit_generates_booking_thumbnail_in_media_storage(self):
        with (
            TemporaryDirectory() as media_root,
            override_settings(MEDIA_ROOT=media_root),
        ):
            source = BytesIO()
            Image.new("RGB", (1200, 600), "blue").save(source, format="PNG")
            pool = ItemPool(name="Camera")
            pool.image.save("camera.png", ContentFile(source.getvalue()), save=False)

            processed = pool.image_processed
            processed.generate()

            processed.open("rb")
            with processed as thumbnail:
                with Image.open(thumbnail) as image:
                    self.assertEqual(image.size, (960, 400))
                    self.assertEqual(image.format, "JPEG")
            self.assertTrue(default_storage.exists(pool.image.name))


class CalendarCompatibilityTests(TestCase):
    def test_subscription_renders_a_parseable_booking_event(self):
        user = User.objects.create_user("abcd12", first_name="Ada")
        pool = ItemPool.objects.create(name="Camera", description="Camera equipment")
        start = timezone.now().replace(microsecond=0) + timedelta(days=1)
        Booking.objects.create(
            user=user,
            pool=pool,
            start=start,
            end=start + timedelta(hours=1),
            description="Photo session",
        )
        subscription = CalendarSubscription.objects.create(user=user)
        response = CalendarFeed()(
            RequestFactory().get("/calendar/"), pk=subscription.pk
        )

        self.assertEqual(response.status_code, 200)
        events = Calendar.from_ical(response.content).walk("VEVENT")
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0].decoded("dtstart"), start)
        self.assertIn("Camera", str(events[0]["summary"]))
        self.assertIn("Photo session", str(events[0]["description"]))
