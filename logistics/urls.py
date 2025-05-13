from django.urls import path
from . import views

app_name = 'logistics'

urlpatterns = [
    # Dashboard
    path('dashboard/', views.LogisticsDashboardView.as_view(), name='dashboard'),
    
    # Shipments
    path('shipments/', views.ShipmentListView.as_view(), name='shipment_list'),
    path('shipments/<int:pk>/', views.ShipmentDetailView.as_view(), name='shipment_detail'),
    path('shipments/create/', views.create_shipment, name='create_shipment'),
    path('shipments/<int:pk>/update/', views.add_shipment_update, name='add_shipment_update'),
    
    # Tracking (public)
    path('track/', views.track_shipment, name='track_shipment'),
    
    # Delivery Zones
    path('zones/', views.DeliveryZoneListView.as_view(), name='delivery_zone_list'),
    
    # Delivery Partners
    path('partners/', views.DeliveryPartnerListView.as_view(), name='delivery_partner_list'),
]
