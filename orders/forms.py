from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Enter your email',
    }))
    confirm_email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Confirm your email',
    }))

    class Meta:
        model = Order
        fields = ('email', 'first_name', 'last_name', 'order_note', 'receiver_phone', 'sender_phone', 'city', 'address',
                  'apartment', 'postal', 'wants_emails')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'First name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last name'
        self.fields['order_note'].widget.attrs['placeholder'] = 'Order note and preferences (optional)'
        self.fields['receiver_phone'].widget.attrs['placeholder'] = 'Receiver phone (optional)'
        self.fields['sender_phone'].widget.attrs['placeholder'] = 'Sender phone'
        self.fields['city'].widget.attrs['placeholder'] = 'Delivery city'
        self.fields['address'].widget.attrs['placeholder'] = 'Delivery address'
        self.fields['apartment'].widget.attrs['placeholder'] = 'Apartment #, etc. (optional)'
        self.fields['postal'].widget.attrs['placeholder'] = 'Postal code'
        self.fields['order_note'].widget.attrs['style'] = 'width: 28.7rem;'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        self.fields['wants_emails'].widget.attrs.clear()

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        confirm_email = cleaned_data.get('confirm_email')

        if email != confirm_email:
            raise forms.ValidationError('Emails did not match')


class TrackOrderForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'placeholder': 'Enter your email',
        'class': 'form-control',
    }))
    order_number = forms.IntegerField(required=True, widget=forms.NumberInput(attrs={
        'placeholder': 'Enter your order number',
        'class': 'form-control',
    }))
