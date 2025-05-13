from django import forms
from .models import DeliveryZone, DeliveryPartner, Shipment, ShipmentUpdate

class ShipmentForm(forms.ModelForm):
    class Meta:
        model = Shipment
        fields = ['order', 'tracking_number', 'delivery_partner', 'delivery_zone', 
                  'status', 'estimated_delivery', 'shipping_cost']
        widgets = {
            'estimated_delivery': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class ShipmentUpdateForm(forms.ModelForm):
    class Meta:
        model = ShipmentUpdate
        fields = ['status', 'location', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

class DeliveryZoneForm(forms.ModelForm):
    class Meta:
        model = DeliveryZone
        fields = ['name', 'description', 'base_fee', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }

class DeliveryPartnerForm(forms.ModelForm):
    class Meta:
        model = DeliveryPartner
        fields = ['name', 'contact_person', 'phone', 'email', 'is_active']

class TrackingForm(forms.Form):
    tracking_number = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter tracking number'
        })
    )
