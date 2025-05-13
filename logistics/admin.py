from django.contrib import admin
from .models import DeliveryZone, DeliveryPartner, Shipment, ShipmentUpdate

admin.site.register(DeliveryZone)
admin.site.register(DeliveryPartner)
admin.site.register(Shipment)
admin.site.register(ShipmentUpdate)