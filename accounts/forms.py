from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Profile


class RegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=100, required=True,
                                  widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}))
    last_name = forms.CharField(max_length=100, required=True,
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}))
    email = forms.EmailField(required=True,
                              widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email address'}))
    # Honeypot: real users never see/fill this (hidden via CSS); bots often do.
    website = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'style': 'position:absolute;left:-9999px;', 'tabindex': '-1', 'autocomplete': 'off'
    }))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Username'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm password'})

    def clean_website(self):
        if self.cleaned_data.get('website'):
            raise forms.ValidationError('Bot submission detected.')
        return ''

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('هذا البريد الإلكتروني مسجل بالفعل.')
        return email


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username or Email'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))


class ProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Profile
        fields = ['avatar', 'phone', 'address', 'city', 'country', 'postal_code']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/png,image/jpeg,image/webp'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
        }

    MAX_AVATAR_SIZE = 3 * 1024 * 1024  # 3 MB
    ALLOWED_CONTENT_TYPES = {'image/jpeg', 'image/png', 'image/webp'}

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if not avatar or not hasattr(avatar, 'content_type'):
            return avatar  # unchanged / cleared / already-saved file

        if avatar.size > self.MAX_AVATAR_SIZE:
            raise forms.ValidationError('حجم الصورة كبير جداً. الحد الأقصى المسموح به 3 ميجابايت.')

        content_type = getattr(avatar, 'content_type', '')
        if content_type not in self.ALLOWED_CONTENT_TYPES:
            raise forms.ValidationError('صيغة الصورة غير مدعومة. المسموح: JPEG, PNG, WEBP فقط.')

        try:
            from PIL import Image
            image = Image.open(avatar)
            image.verify()
        except Exception:
            raise forms.ValidationError('الملف المرفوع ليس صورة صالحة.')
        avatar.seek(0)
        return avatar
