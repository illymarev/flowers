from django import forms
from .models import Account


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter password',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Confirm password',
    }))

    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Enter email'
    }))
    confirm_email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Confirm email'
    }))

    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'wants_emails', 'password')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter first name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter last name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter phone number'
        self.fields['wants_emails'].widget.attrs['class'] = 'small-text'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['wants_emails'].widget.attrs.clear()

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        confirm_email = cleaned_data.get('confirm_email')
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if email != confirm_email:
            raise forms.ValidationError('Emails did not match')

        if password != confirm_password:
            raise forms.ValidationError('Passwords did not match')


class EditProfile(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name', 'last_name', 'phone_number', 'wants_emails')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['wants_emails'].widget.attrs.clear()
