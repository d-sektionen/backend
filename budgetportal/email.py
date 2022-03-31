from django.core.mail import get_connection
from django.core.mail.message import EmailMessage
from django.core.mail.backends.smtp import EmailBackend

NOREPLY_EMAIL = "noreply.budget@d-sektionen.se"


def send(subject: str, body: str, to: str):
    """Sends an e-mail from the budget app's noreply address."""
    print("About to start e-mail connection...")
    with get_connection(
        host="smtp.gmail.com",
        port=587,
        username=NOREPLY_EMAIL, 
        password="budgetteringsportalen2022dsektionen",
        use_tls=True,
    ) as connection:
        print("Started e-mail connection!")
        print(f"About to send e-mail to {to}...")
        EmailMessage(
            subject, 
            body, 
            NOREPLY_EMAIL, 
            [to],
            connection=connection
        ).send()
        print(f"Sent e-mail to {to}!")
