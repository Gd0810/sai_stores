from django import forms
from .models import Address, Feedback

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['name', 'mobile', 'locality', 'city', 'state', 'zipcode']  # Removed 'user'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_name'}),
            'mobile': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_mobile'}),
            'locality': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_locality'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_city'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_state'}),
            'zipcode': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_zipcode'}),
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['rating', 'comment']
