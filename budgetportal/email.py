from django.core.mail import get_connection
from django.core.mail.message import EmailMessage

subject = ""
body = ""
email_from = "noreply.budget@d-sektionen.se"
to = ""

with get_connection(
    host="smtp.google.com", 
    port=587, 
    username="noreply.budget@d-sektionen.se", 
    password="budgetteringsportalen2022dsektionen", 
    use_tls=True
) as connection:
    EmailMessage(subject, body, email_from, [to],
                 connection=connection).send()