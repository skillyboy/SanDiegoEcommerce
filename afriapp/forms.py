from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import *
from django.contrib.auth.forms import UserChangeForm

class AccountUpdateForm(UserChangeForm):
    password = forms.CharField(required=False, widget=forms.PasswordInput, label="New Password")

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']  # Include other fields as needed

    def clean_password(self):
        # This method is needed to avoid requiring the password during updates
        return self.initial['password']

    def save(self, commit=True):
        user = super().save(commit=False)
        # If a new password is provided, set it
        if self.cleaned_data['password']:
            user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user 
    
class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            # 'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name','price', 'description', 'stock_quantity', 'image']

        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Product Name'}),
            # 'category': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Price'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Product Description'}),
            'stock_quantity': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Stock Quantity'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category Name'}),
        }        
        
class ShopCartForm(forms.ModelForm):
    class Meta:
        model = ShopCart
        fields = ('quantity',)
        widgets = {
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})
        }





class CheckoutForm(forms.Form): 
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)
    company = forms.CharField(max_length=100, required=False)
    country = forms.CharField(max_length=100, required=True)
    city = forms.CharField(max_length=100, required=True)
    phone = forms.CharField(max_length=20, required=True)
    stripe_token = forms.CharField(widget=forms.HiddenInput, required=True)  # Hidden Stripe token field
    
    # Shipping-related fields
    address = forms.CharField(widget=forms.Textarea, required=True)
    postal_code = forms.CharField(max_length=10, required=True)
    
    # Shipping options
    shipping_option = forms.ChoiceField(
        choices=[
            ('standard', 'Standard Shipping'),
            ('express', 'Express Shipping'),
            ('short', '1 - 2 Day Shipping'),
        ],
        widget=forms.RadioSelect,
        required=True
    )
    
    # # Credit card details
    # card_number = forms.CharField(max_length=16, required=True, min_length=16, label='Card Number')
    # card_name = forms.CharField(max_length=100, required=True, label='Cardholder Name')
    
    # expiry_month = forms.ChoiceField(
    #     choices=[(str(i), month) for i, month in enumerate(
    #         ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'], 1
    #     )],
    #     required=True,
    #     label='Expiry Month'
    # )
    

    # Clean method for additional validation
    def clean(self):
        cleaned_data = super().clean()
        stripe_token = cleaned_data.get('stripe_token')
        
        # Ensure Stripe token exists before proceeding
        if not stripe_token:
            raise forms.ValidationError("Stripe token is missing")
        
        # Additional validation can be added here if necessary
        
        return cleaned_data

# to update address/payment info
class PaymentInfoForm(forms.ModelForm):
    class Meta:
        model = PaymentInfo
        fields = [
            'amount', 'first_name', 'last_name', 'phone', 'address', 'city', 
            'state', 'postal_code', 'country', 'payment_method'
        ]
        widgets = {
            'payment_method': forms.Select(choices=PaymentInfo._meta.get_field('payment_method').choices)
        }