import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class SessionCookieMiddleware(MiddlewareMixin):
    """
    Middleware to sync session values to cookies for JavaScript access.
    This allows the frontend to know if an email has been collected without
    making an AJAX request.
    """
    
    def process_response(self, request, response):
        """
        Process the response before it's sent to the client.
        Sync important session values to cookies.
        """
        try:
            # Sync email_collected flag to cookie
            if hasattr(request, 'session') and 'email_collected' in request.session:
                email_collected = request.session.get('email_collected', False)
                response.set_cookie('email_collected', str(email_collected).lower(), max_age=86400)  # 1 day
                
            # Sync cart_count to cookie
            if hasattr(request, 'session') and 'cart_count' in request.session:
                cart_count = request.session.get('cart_count', 0)
                response.set_cookie('cart_count', str(cart_count), max_age=86400)  # 1 day
        except Exception as e:
            logger.error(f"Error in SessionCookieMiddleware: {str(e)}")
            
        return response
