from django import forms

from .models import UserMetadata


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserMetadata
        fields = ['bio', 'interests', 'drives']  # add any other fields you want editable
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'cols': 40}),
            'interests': forms.TextInput(attrs={'size': 50}),
            'drives': forms.Select(choices=[(True, 'Yes'), (False, 'No')])
        }
        help_texts = {
            'bio': 'Tell us something interesting about yourself.',
            'interests': 'What are your hobbies or interests?',
            'drives': 'Do you drive?'
        }