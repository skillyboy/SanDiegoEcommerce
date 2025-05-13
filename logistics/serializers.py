from rest_framework import serializers
from .models import DeliveryZone, DeliveryPartner, Shipment, ShipmentUpdate
from afriapp.serializers import OrderSerializer

class DeliveryZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryZone
        fields = '__all__'

class DeliveryPartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryPartner
        fields = '__all__'

class ShipmentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShipmentUpdate
        fields = '__all__'

class ShipmentSerializer(serializers.ModelSerializer):
    updates = ShipmentUpdateSerializer(many=True, read_only=True)
    delivery_partner = DeliveryPartnerSerializer(read_only=True)
    delivery_zone = DeliveryZoneSerializer(read_only=True)
    
    class Meta:
        model = Shipment
        fields = '__all__'
        
class ShipmentTrackingSerializer(serializers.ModelSerializer):
    updates = ShipmentUpdateSerializer(many=True, read_only=True)
    status_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Shipment
        fields = ['tracking_number', 'status', 'status_display', 'estimated_delivery', 
                  'actual_delivery', 'created_at', 'updated_at', 'updates']
    
    def get_status_display(self, obj):
        return obj.get_status_display()
