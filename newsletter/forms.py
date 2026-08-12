from django import forms
from .models import Subscriber

HONEYPOT_ATTRS = {'style': 'position:absolute;left:-9999px;', 'tabindex': '-1', 'autocomplete': 'off'}


class SubscriberForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.TextInput(attrs=HONEYPOT_ATTRS))

    class Meta:
        model = Subscriber
        fields = ['name', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'}),
        }

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise forms.ValidationError('Bot submission detected.')
        return ''
