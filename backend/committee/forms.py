from django import forms
from django.contrib.auth.models import User
from django.contrib.admin.widgets import FilteredSelectMultiple

from ..committee.models import Committee


class CommitteeForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        required=False,
        widget=FilteredSelectMultiple(verbose_name="Members", is_stacked=False),
    )

    class Meta:
        model = Committee
        fields = (
            "name",
            "description",
            "members",
            "treasurer",
            "treasurer_email",
            "chair",
            "chair_email",
        )
        fieldsets = (
            (None, {"fields": ("name", "description", "members")}),
            ("Treasurer", {"fields": ("treasurer", "treasurer_email")}),
            ("Chair", {"fields": ("chair", "chair_email")}),
        )

    def clean(self):
        treasurer = self.cleaned_data.get("treasurer")
        treasurer_email = self.cleaned_data.get("treasurer_email")

        # Assert that BOTH the treasurer and their e-mail have been changed
        if (
            "treasurer_email" not in self.changed_data
            and "treasurer" in self.changed_data
        ):
            raise forms.ValidationError(
                {
                    "treasurer_email": f"The treasurer has changed, but not the e-mail. Did you mean {treasurer.first_name}.{treasurer.last_name}@d-sektionen.se?"
                }
            )

        # Assert that the treasurer e-mail is NOT empty
        if not treasurer_email:
            raise forms.ValidationError(
                {
                    "treasurer_email": f"The treasurer e-mail can not be empty. Did you mean {treasurer.first_name}.{treasurer.last_name}@d-sektionen.se?"
                }
            )

        if self.cleaned_data.get("treasurer") not in self.cleaned_data.get("members"):
            raise forms.ValidationError(
                {"treasurer": "Contact needs to be a member of the committee"}
            )  # TODO: should not need to be a member of the committee
        return super().clean()
