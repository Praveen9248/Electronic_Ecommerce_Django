# your_app/forms.py
from django import forms
from .models import Category, Brand, RepairProduct, ServiceRequest, User
from django.contrib.auth.forms import UserCreationForm

class ProductFilterForm(forms.Form):
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    brand = forms.ModelChoiceField(
        queryset=Brand.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'role')

class UpdateServiceRequestStatusForm(forms.Form):
    status = forms.ChoiceField(
        choices=ServiceRequest.STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )
    work_done = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )
    parts_used = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        required=False
    )
    final_cost = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

class ServiceRequestForm(forms.ModelForm):
    class Meta:
        model = ServiceRequest
        fields = ['repair_product', 'issue_description', 'customer_notes', 'pickup_option', 'shipping_address']
        widgets = {
            'issue_description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'customer_notes': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'shipping_address': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'repair_product': forms.Select(attrs={'class': 'form-control'}),
            'pickup_option': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class RepairProductForm(forms.ModelForm):
    class Meta:
        model = RepairProduct
        fields = ['device_model', 'brand', 'serial_number']
        widgets = {
            'device_model': forms.TextInput(attrs={'class': 'form-control'}),
            'brand': forms.Select(attrs={'class': 'form-control'}),
            'serial_number': forms.TextInput(attrs={'class': 'form-control'}),
        }