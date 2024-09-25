from rest_framework import serializers
from .models import Product, Wishlist, Review, Payment, ShopCart, Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class ShopCartSerializer(serializers.ModelSerializer):
    product = ProductSerializer()

    class Meta:
        model = ShopCart
        fields = [
            'id',
            'product',
            'quantity',
            'total'
        ]