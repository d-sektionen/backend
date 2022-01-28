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
        fields = 'id', 'name', 'description', 'members', 'contact',
    
    def clean(self):
        if self.cleaned_data.get('contact') not in self.cleaned_data.get('members'):
            raise forms.ValidationError({'contact': 'Contact needs to be a member of the committee'})
        return super().clean()