from .models import *


def context_processor(request):
    from decimal import Decimal
    from django.db.models import Sum, F

    services = Service.objects.all()
    cart_count = 0  # Default to 0
    cart = None
    subtotal = 0
    vat = 0
    total = 0

    # Check if user is authenticated
    if request.user.is_authenticated:
        cart = ShopCart.objects.filter(user=request.user, paid_order=False, quantity__gt=0)
        cart_count = cart.aggregate(total_items=Sum('quantity'))['total_items'] or 0
    # For guest users, use session key
    else:
        # Get or create session key
        if not request.session.session_key:
            request.session.create()

        session_key = request.session.session_key
        cart = ShopCart.objects.filter(session_key=session_key, user=None, paid_order=False, quantity__gt=0)
        cart_count = cart.aggregate(total_items=Sum('quantity'))['total_items'] or 0

        # Check if we have a guest email in the session
        guest_email = request.session.get('guest_email')
        if guest_email:
            # Store it for easy access in templates
            request.session['has_guest_email'] = True

    # Store cart count in session for easy access
    request.session['cart_count'] = cart_count

    # Calculate cart summary if there are items
    if cart_count > 0:
        # Calculate subtotal
        subtotal = sum(item.calculate_total_price() for item in cart)

        # Calculate VAT and total
        vat = Decimal('0.075') * Decimal(str(subtotal))
        total = subtotal + vat

        # Convert to float for template display
        subtotal = float(subtotal)
        vat = float(vat)
        total = float(total)

    context = {
        'services': services,
        'cart': cart,
        'cart_count': cart_count,
        'subtotal': subtotal,
        'vat': vat,
        'total': total,
    }

    return context




def banner(request):
    try:
        from .models import Carousel
        slide = Carousel.objects.filter(pk=1).first()
        slide2 = Carousel.objects.filter(pk=2).first()
        slide3 = Carousel.objects.filter(pk=3).first()

        context = {
            'slide': slide,
            'slide2': slide2,
            'slide3': slide3,
        }
    except Exception as e:
        print(f"Error loading carousel slides: {e}")
        context = {
            'slide': None,
            'slide2': None,
            'slide3': None,
        }

    return context
