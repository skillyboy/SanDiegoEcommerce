from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.views.generic import TemplateView, ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.core.paginator import Paginator

from .models import DeliveryZone, DeliveryPartner, Shipment, ShipmentUpdate
from afriapp.models import Order, Customer

# Dashboard view for logistics
class LogisticsDashboardView(TemplateView):
    template_name = 'logistics/dashboard.html'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_shipments'] = Shipment.objects.filter(status='pending').count()
        context['in_transit_shipments'] = Shipment.objects.filter(status='in_transit').count()
        context['delivered_shipments'] = Shipment.objects.filter(status='delivered').count()
        context['total_shipments'] = Shipment.objects.all().count()
        return context

# Shipment list view
class ShipmentListView(ListView):
    model = Shipment
    template_name = 'logistics/shipment_list.html'
    context_object_name = 'shipments'
    paginate_by = 10

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()
        status_filter = self.request.GET.get('status', '')
        search_query = self.request.GET.get('search', '')

        if status_filter:
            queryset = queryset.filter(status=status_filter)

        if search_query:
            queryset = queryset.filter(
                Q(tracking_number__icontains=search_query) |
                Q(order__order_no__icontains=search_query) |
                Q(delivery_partner__name__icontains=search_query)
            )

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['status_filter'] = self.request.GET.get('status', '')
        context['search_query'] = self.request.GET.get('search', '')
        return context

# Shipment detail view
class ShipmentDetailView(DetailView):
    model = Shipment
    template_name = 'logistics/shipment_detail.html'
    context_object_name = 'shipment'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['updates'] = self.object.updates.all().order_by('-timestamp')
        context['delivery_partners'] = DeliveryPartner.objects.filter(is_active=True)
        context['delivery_zones'] = DeliveryZone.objects.filter(is_active=True)
        return context

# Add shipment update
@login_required
def add_shipment_update(request, pk):
    shipment = get_object_or_404(Shipment, pk=pk)

    if request.method == 'POST':
        status = request.POST.get('status')
        location = request.POST.get('location')
        notes = request.POST.get('notes')

        if status:
            update = ShipmentUpdate.objects.create(
                shipment=shipment,
                status=status,
                location=location,
                notes=notes
            )

            # Update the shipment status
            shipment.status = status
            shipment.save()

            messages.success(request, 'Shipment update added successfully.')
            return redirect('shipment_detail', pk=shipment.pk)
        else:
            messages.error(request, 'Status is required.')

    return redirect('shipment_detail', pk=shipment.pk)

# Create new shipment
@login_required
def create_shipment(request):
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        tracking_number = request.POST.get('tracking_number')
        delivery_partner_id = request.POST.get('delivery_partner')
        delivery_zone_id = request.POST.get('delivery_zone')
        shipping_cost = request.POST.get('shipping_cost', 0)

        try:
            order = Order.objects.get(id=order_id)
            delivery_partner = None
            delivery_zone = None

            if delivery_partner_id:
                delivery_partner = DeliveryPartner.objects.get(id=delivery_partner_id)

            if delivery_zone_id:
                delivery_zone = DeliveryZone.objects.get(id=delivery_zone_id)

            shipment = Shipment.objects.create(
                order=order,
                tracking_number=tracking_number,
                delivery_partner=delivery_partner,
                delivery_zone=delivery_zone,
                shipping_cost=shipping_cost,
                status='pending'
            )

            messages.success(request, f'Shipment created successfully with tracking number {tracking_number}.')
            return redirect('shipment_detail', pk=shipment.pk)

        except Order.DoesNotExist:
            messages.error(request, 'Order not found.')
        except Exception as e:
            messages.error(request, f'Error creating shipment: {str(e)}')

    # Get all orders that don't have shipments yet
    orders = Order.objects.filter(shipments__isnull=True)
    delivery_partners = DeliveryPartner.objects.filter(is_active=True)
    delivery_zones = DeliveryZone.objects.filter(is_active=True)

    context = {
        'orders': orders,
        'delivery_partners': delivery_partners,
        'delivery_zones': delivery_zones
    }

    return render(request, 'logistics/create_shipment.html', context)

# Customer tracking page (public)
def track_shipment(request):
    tracking_number = request.GET.get('tracking_number', '')
    shipment = None

    if tracking_number:
        try:
            shipment = Shipment.objects.get(tracking_number=tracking_number)
        except Shipment.DoesNotExist:
            messages.error(request, 'Shipment not found with the provided tracking number.')

    context = {
        'tracking_number': tracking_number,
        'shipment': shipment,
        'updates': shipment.updates.all().order_by('-timestamp') if shipment else None
    }

    # Use the new modern tracking template
    return render(request, 'logistics/track.html', context)

# Delivery zones management
class DeliveryZoneListView(ListView):
    model = DeliveryZone
    template_name = 'logistics/delivery_zone_list.html'
    context_object_name = 'zones'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)

# Delivery partners management
class DeliveryPartnerListView(ListView):
    model = DeliveryPartner
    template_name = 'logistics/delivery_partner_list.html'
    context_object_name = 'partners'

    @method_decorator(login_required)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
