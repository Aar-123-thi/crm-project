from django import forms
from .models import Customer, Lead, Purchase, Profile, Product

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'phone', 'email']

class LeadForm(forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['name', 'phone', 'email', 'status']

class PurchaseForm(forms.ModelForm):
    class Meta:
        model = Purchase
        fields = ['customer', 'product', 'quantity']

class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']