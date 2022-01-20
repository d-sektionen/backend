from django import forms
from django.contrib.auth.models import User
from django.contrib.admin.widgets import FilteredSelectMultiple

from committee.models import Committee


class CommitteeForm(forms.ModelForm):
    members = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(), 
        required=False,
        widget=FilteredSelectMultiple(verbose_name='Members', is_stacked=False)
    )

    class Meta:
        model = Committee
        fields = 'id', 'name', 'members'