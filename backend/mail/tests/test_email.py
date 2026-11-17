from html.parser import HTMLParser

from django.core import mail as django_mail
from django.core.mail.backends.locmem import EmailBackend
from django.test import SimpleTestCase, TestCase, override_settings
from post_office import mail
from post_office.connections import connections
from post_office.models import Email, STATUS

from backend.app import settings_shared
from backend.app.utils import render_email
from backend.budgetportal.email import NOREPLY_EMAIL, send as send_budget_email


class RecordingBackend(EmailBackend):
    deliveries = []

    def send_messages(self, messages):
        self.deliveries.append((self.alias, [message.subject for message in messages]))
        return super().send_messages(messages)


class FailingBackend(EmailBackend):
    def send_messages(self, messages):
        raise OSError("Synthetic SMTP failure")


TEST_MAILERS = {
    **settings_shared.MAILERS,
    "smtp": {"BACKEND": "backend.mail.tests.test_email.RecordingBackend"},
    "budget": {"BACKEND": "backend.mail.tests.test_email.RecordingBackend"},
}


class EmailRenderingTests(SimpleTestCase):
    def test_rendering_preserves_inline_spaces_and_escapes_user_content(self):
        html = (
            '<p>\n  <span>{{ name }}</span> <a href="{{ url }}">Open booking</a>\n</p>'
        )
        templates = {
            "message.subject.txt": "  Booking: {{ name }}\n",
            "message.html": html,
        }
        with override_settings(
            TEMPLATES=[
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "OPTIONS": {
                        "loaders": [
                            ("django.template.loaders.locmem.Loader", templates)
                        ]
                    },
                }
            ]
        ):
            subject, body = render_email(
                "message",
                {"name": "Åsa <guest>", "url": "https://example.com/?a=1&b=2"},
            )
        self.assertEqual(subject, "Booking: Åsa &lt;guest&gt;")

        # Minification may rewrite entities and omit attribute quotes.
        class ContentParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.text = ""
                self.links = []

            def handle_data(self, data):
                self.text += data

            def handle_starttag(self, tag, attrs):
                if tag == "a":
                    self.links.append(dict(attrs)["href"])

        parsed = ContentParser()
        parsed.feed(body)
        self.assertEqual(parsed.text, "Åsa <guest> Open booking")
        self.assertEqual(parsed.links, ["https://example.com/?a=1&b=2"])
        self.assertNotIn("\n", body)


@override_settings(MAILERS=TEST_MAILERS)
class MailerRoutingTests(TestCase):
    def setUp(self):
        connections.close()
        self.addCleanup(connections.close)
        RecordingBackend.deliveries = []

    def test_default_mailer_queues_and_worker_delivers_without_requeuing(self):
        count = Email.objects.count()
        django_mail.EmailMessage(
            subject="Queued message",
            body="Body",
            from_email="sender@example.com",
            to=["recipient@example.com"],
        ).send(using="default")
        queued = Email.objects.get(subject="Queued message")
        self.assertEqual(queued.status, STATUS.queued)
        self.assertEqual(len(django_mail.outbox), 0)

        self.assertEqual(mail.send_queued(processes=1), (1, 0, 0))

        queued.refresh_from_db()
        self.assertEqual(queued.status, STATUS.sent)
        self.assertEqual(Email.objects.count(), count + 1)
        self.assertEqual(RecordingBackend.deliveries, [("smtp", ["Queued message"])])
        self.assertEqual(django_mail.outbox[0].to, ["recipient@example.com"])

    def test_old_blank_and_default_backend_aliases_deliver_through_smtp(self):
        messages = [
            Email.objects.create(
                subject=f"Legacy {alias or 'blank'}",
                from_email="sender@example.com",
                to=["recipient@example.com"],
                message="Existing queued content",
                backend_alias=alias,
                status=STATUS.queued,
            )
            for alias in ("", "default")
        ]
        self.assertEqual(mail.send_queued(processes=1), (2, 0, 0))
        for message in messages:
            message.refresh_from_db()
            self.assertEqual(message.status, STATUS.sent)
        self.assertTrue(
            all(alias == "smtp" for alias, _ in RecordingBackend.deliveries)
        )

    def test_existing_post_office_calls_keep_immediate_delivery_and_bcc(self):
        message = mail.send(
            recipients=[],
            sender="sender@example.com",
            bcc=["hidden@example.com"],
            subject="Newsletter",
            html_message="<p>Hello</p>",
            priority="now",
        )
        self.assertEqual(message.status, STATUS.sent)
        self.assertEqual(RecordingBackend.deliveries, [("smtp", ["Newsletter"])])
        self.assertEqual(django_mail.outbox[0].bcc, ["hidden@example.com"])

    def test_budget_mail_bypasses_queue_and_uses_its_own_mailer(self):
        count = Email.objects.count()
        send_budget_email("Budget update", "Approved", "treasurer@example.com")
        self.assertEqual(RecordingBackend.deliveries, [("budget", ["Budget update"])])
        self.assertEqual(Email.objects.count(), count)
        self.assertEqual(django_mail.outbox[0].from_email, NOREPLY_EMAIL)
        self.assertEqual(django_mail.outbox[0].to, ["treasurer@example.com"])

    @override_settings(
        MAILERS={
            **TEST_MAILERS,
            "smtp": {"BACKEND": "backend.mail.tests.test_email.FailingBackend"},
        }
    )
    def test_delivery_failure_is_recorded_without_requeuing(self):
        queued = mail.send(
            "recipient@example.com",
            "sender@example.com",
            subject="Failure",
            message="Body",
            priority="medium",
        )
        with self.assertLogs("post_office", level="ERROR"):
            self.assertEqual(mail.send_queued(processes=1), (0, 1, 0))
        queued.refresh_from_db()
        self.assertEqual(queued.status, STATUS.failed)
