from .models import Committee


def get_deg_committee():
    """Returns the committee object representing DEG."""
    # TODO: change the name to the proper one when deployed
    return Committee.objects.get(name="deg")


