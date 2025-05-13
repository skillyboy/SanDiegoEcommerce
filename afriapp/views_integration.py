"""
Integration views for connecting the main application with the agrolinker app.
These views provide a bridge between the e-commerce functionality and the agricultural services.
"""

from django.shortcuts import render, redirect
from django.views.generic import TemplateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.conf import settings

from project.microservice_config import MicroserviceClient

class AgroLinkerDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard view for the AgroLinker integration"""
    template_name = 'afriapp/agro_dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add AgroLinker data to the context
        context['page_title'] = 'Agricultural Services'
        context['is_agro_dashboard'] = True
        
        # Get data from the microservice if available
        try:
            # Fetch farm data if the user is a farmer
            farm_data = MicroserviceClient.get(
                f"{MicroserviceClient.API_ENDPOINTS['farm']}",
                params={'user_id': self.request.user.id}
            )
            context['farm_data'] = farm_data
            
            # Fetch market data
            market_data = MicroserviceClient.get(
                f"{MicroserviceClient.API_ENDPOINTS['market']}/summary"
            )
            context['market_data'] = market_data
            
        except Exception as e:
            if settings.DEBUG:
                print(f"Error fetching AgroLinker data: {e}")
            context['error_message'] = "Unable to fetch agricultural data at this time."
        
        return context

class MarketPriceView(TemplateView):
    """View for displaying market prices"""
    template_name = 'afriapp/market_prices.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add market price data to the context
        context['page_title'] = 'Market Prices'
        
        # Get crop type from query parameters
        crop_type = self.request.GET.get('crop_type', 'all')
        
        # Get data from the microservice
        try:
            if crop_type != 'all':
                # Get price for specific crop
                price_data = MicroserviceClient.get_price_discovery(crop_type)
                context['price_data'] = price_data
                context['crop_type'] = crop_type
            else:
                # Get prices for all crops
                price_data = MicroserviceClient.get(
                    f"{MicroserviceClient.API_ENDPOINTS['market']}/prices"
                )
                context['price_data'] = price_data
                context['crop_type'] = 'all'
                
        except Exception as e:
            if settings.DEBUG:
                print(f"Error fetching market prices: {e}")
            context['error_message'] = "Unable to fetch market prices at this time."
        
        return context

def price_discovery_api(request):
    """API endpoint for price discovery"""
    crop_type = request.GET.get('crop_type')
    
    if not crop_type:
        return JsonResponse({'error': 'Crop type is required'}, status=400)
    
    # Get price data from the microservice
    price_data = MicroserviceClient.get_price_discovery(crop_type)
    
    return JsonResponse(price_data)

def process_thrift_data_api(request):
    """API endpoint for processing thrift data"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    data = request.POST.get('data')
    
    if not data:
        return JsonResponse({'error': 'Data is required'}, status=400)
    
    # Process thrift data through the microservice
    result = MicroserviceClient.process_thrift_data(data)
    
    return JsonResponse(result)
