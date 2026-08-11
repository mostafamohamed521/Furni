from django import forms
from .models import ContactMessage

HONEYPOT_ATTRS = {'style': 'position:absolute;left:-9999px;', 'tabindex': '-1', 'autocomplete': 'off'}


class ContactForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.TextInput(attrs=HONEYPOT_ATTRS))

    class Meta:
        model = ContactMessage
        fields = ['first_name', 'last_name', 'email', 'message']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'fname'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'lname'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'id': 'email'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'id': 'message', 'rows': 5}),
        }

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise forms.ValidationError('Bot submission detected.')
        return ''
