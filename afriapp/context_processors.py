from .models import *


def context_processor(request):
    services = Service.objects.all()
    cart_count = 0  # Default to 0 if user is not authenticated
    cart = None
    
    # Check if user is authenticated
    if request.user.is_authenticated:
        cart = ShopCart.objects.filter(user=request.user, paid_order=False)
        cart_count = cart.count()  # Use .count() method

    # Debugging: Print cart count
    print(f"User: {request.user.username if request.user.is_authenticated else 'Anonymous'}, Cart Count: {cart_count}")

    context = {
        'services': services,
        'cart': cart,
        'cart_count': cart_count,
    }

    return context


    

def banner(request):
    slide= Carousel.objects.get(pk=1)
    slide2=Carousel.objects.get(pk=2)
    slide3=Carousel.objects.get(pk=3)


    context={
        'slide':slide,
        'slid2':slide2,
        'slide3':slide3,
    }

    return context