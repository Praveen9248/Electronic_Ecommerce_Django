from django.shortcuts import get_object_or_404
from .models import Cart

def user_data(request):
    context = {}
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_item_count = cart.items.count()
        except Cart.DoesNotExist:
            cart_item_count = 0
        context['cart_item_count'] = cart_item_count
        context['user_name'] = request.user.get_username()
    else:
        context['cart_item_count'] = 0
        context['user_name'] = None

    return context