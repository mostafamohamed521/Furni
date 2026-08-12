from django import forms
from .models import Order

COUNTRY_CHOICES = [
    ('', 'Select a country'),
    ('EG', 'Egypt'),
    ('SA', 'Saudi Arabia'),
    ('AE', 'United Arab Emirates'),
    ('KW', 'Kuwait'),
    ('QA', 'Qatar'),
    ('BH', 'Bahrain'),
    ('JO', 'Jordan'),
    ('MA', 'Morocco'),
    ('DZ', 'Algeria'),
    ('IQ', 'Iraq'),
]


class OrderCreateForm(forms.ModelForm):
    country = forms.ChoiceField(choices=COUNTRY_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Order
        fields = [
            'country', 'first_name', 'last_name', 'company_name', 'address', 'apartment',
            'state', 'postal_code', 'email', 'phone', 'notes',
            'ship_to_different_address', 'shipping_address', 'shipping_city',
            'shipping_country', 'shipping_postal_code', 'payment_method',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'company_name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street address'}),
            'apartment': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apartment, suite, unit etc. (optional)'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Write your notes here...'}),
            'shipping_address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Street address'}),
            'shipping_city': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_country': forms.TextInput(attrs={'class': 'form-control'}),
            'shipping_postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'ship_to_different_address': forms.CheckboxInput(),
            'payment_method': forms.RadioSelect(),
        }

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        digits = ''.join(ch for ch in phone if ch.isdigit() or ch == '+')
        if len(digits) < 8:
            raise forms.ValidationError('Please enter a valid phone number.')
        return phone


class CouponApplyForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Coupon Code'}))


class TrackOrderForm(forms.Form):
    order_number = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. FRN-A1B2C3D4'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email used for the order'}))
