from django import forms
from .models import ReviewRating


class ReviewForm(forms.ModelForm):
    class Meta:
        model = ReviewRating
        fields = ['review', 'rating', 'display_name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['display_name'].initial = 'Anonymous'
