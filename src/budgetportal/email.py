from django.contrib.auth.models import User
from django.core.mail import get_connection
from django.core.mail.message import EmailMessage

from ..committee.models import Committee
from .models import BudgetEntry


NOREPLY_EMAIL = "noreply.budget@d-sektionen.se"


def send(subject: str, body: str, *recipient_emails: str):
    """
    Sends an e-mail to some recipients from the budget app's noreply address.
    """
    with get_connection(
        host="smtp.gmail.com",
        port=587,
        username=NOREPLY_EMAIL,
        password="budgetteringsportalen2022dsektionen",
        use_tls=True,
    ) as connection:
        EmailMessage(
            subject,
            body,
            NOREPLY_EMAIL,
            recipient_emails,
            connection=connection
        ).send()


def send_new_entry_mails(creator: User, entry: BudgetEntry):
    # Send e-mail to the concerned committee's treasurer
    treasurer_subject = "Ett nytt personligt utlägg finns att granska"
    treasurer_body = "Hej!\n"+str(creator.get_full_name()) +" har fyllt ut ett nytt personligt utlägg som gäller ditt utskott. Gå in och granska det här: [länk]"  # TODO: fill in link
    send(treasurer_subject, treasurer_body, entry.committee.treasurer_email)

    # Send e-mail to all DEG members
    deg_committee = Committee.objects.filter(name="deg").first()
    if deg_committee:
        deg_subject = "Ett nytt personligt utlägg finns att granska"
        deg_body = "Hej!\nDet finns ett nytt personligt utlägg för" + str(entry.committee.name) + "för dig att granska och bokföra, du hittar utlägget här: [länk]"  # TODO: fill in link
        deg_emails = [str(x.first_name)+"."+str(x.last_name)+"@d-sektionen.se" for x in deg_committee.members.all()]
        send(deg_subject, deg_body, *deg_emails)
    else:
        print("A committee for DEG does not exist in the backend.")


def send_entry_payed_mail(payer: User, entry: BudgetEntry):
    subject = "Ditt personliga utlägg har utbetalats"
    body = f"Hej!\nDitt personliga utlägg för {entry.committee.name} har betalats ut av {payer.get_full_name()}, pengarna bör finnas på ditt konto inom 1-2 bankdagar."
    send(subject, body, entry.user.email)


def send_entry_denied_mail(denier: User, entry: BudgetEntry):
    subject = "Ditt personliga utlägga har nekats"
    body = f"Hej!\nDitt personliga utlägg för {entry.committee.name} har nekats av {denier.get_full_name()}. Logga in på ditt konto på budgetportalen för att se motiveringen."
    send(subject, body, entry.user.email)


def send_unpayed_entries_mail(entry: BudgetEntry):
    unpayed_entry_count = BudgetEntry.objects.filter(payed=False, approvedDeg=True, committee__treasurer=entry.committee.treasurer).count()
    subject = str(unpayed_entry_count) + "bokförda utlägg finns att betala ut"
    body = "Hej! Det finns "+str(unpayed_entry_count)+" nya bokförda personliga utlägg för dig att betala ut. Du kommer åt dem här: [länk]"  # TODO: fill in link
    send(subject, body, entry.committee.treasurer_email)
