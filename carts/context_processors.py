from .views import _cart_id
from .models import Cart, CartItem


def active_cart(request):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))

    if request.user.is_authenticated:
        try:
            cart_items = CartItem.objects.filter(user=request.user, product__is_sold=False)
        except CartItem.DoesNotExist:
            cart_items = None
    else:
        try:
            cart_items = CartItem.objects.filter(cart=cart, is_active=True, product__is_sold=False)
        except CartItem.DoesNotExist:
            cart_items = None

    context = {'cart': cart,
               'cart_items': cart_items}
    return context
