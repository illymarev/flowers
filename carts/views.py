from django.shortcuts import render, redirect, reverse, get_object_or_404
from products.models import Product
from .models import Cart, CartItem
from orders.forms import OrderForm
from orders.models import Order
from accounts.models import Account
import datetime


# Create your views here.
def _cart_id(request):
    cart_id = request.session.session_key
    if not cart_id:
        cart_id = request.session.create()
    return cart_id


def add_to_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    # no check needed since context processor does the checking and creates a cart in case the check fails
    users_cart = Cart.objects.get(cart_id=_cart_id(request))

    if request.user.is_authenticated:
        if CartItem.objects.filter(product=product, user=request.user).exists():
            pass
        else:
            cart_item = CartItem.objects.create(product=product, user=request.user)
            cart_item.save()
    else:
        if CartItem.objects.filter(product=product, cart=users_cart).exists():
            pass
            # since bouquets/plants are designed so that they are limited in quantity
            # (for example, there's only one bouquet
            # with white and red roses), I do not need to increment the quantity
            # because the quantity of the product in real life is always 1
        else:
            cart_item = CartItem.objects.create(product=product, cart=users_cart)
            cart_item.save()
    return redirect(reverse('cart'))


def remove_from_cart(request, product_id, cart_item_id):
    users_cart = Cart.objects.get(cart_id=_cart_id(request))
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(user=request.user, id=cart_item_id, product=product)
    else:
        cart_item = CartItem.objects.get(cart=users_cart, product=product)
    cart_item.delete()
    return redirect(reverse('cart'))


def cart(request):
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
            cart_items = CartItem.objects.filter(cart=cart, product__is_sold=False)
        except CartItem.DoesNotExist:
            cart_items = None
    total_without_tax = 0
    for item in cart_items:
        total_without_tax += item.product.price
    tax = total_without_tax / 100 * 15
    if total_without_tax >= 150:
        delivery = 0
    else:
        delivery = 15
    total_with_tax_and_shipping = total_without_tax + tax + delivery
    context = {
        'total_without_tax': total_without_tax,
        'tax': tax,
        'delivery': delivery,
        'total': total_with_tax_and_shipping
    }
    return render(request, 'carts/cart.html', context)


def checkout(request):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except Cart.DoesNotExist:
        cart = Cart.objects.create(cart_id=_cart_id(request))

    if request.user.is_authenticated:
        try:
            cart_items = CartItem.objects.filter(user=request.user, product__is_sold=False)
        except CartItem.DoesNotExist:
            cart_items = None

        users_account = Account.objects.get(email=request.user.email)
        bonus_points = users_account.bonus_points
    else:
        bonus_points = 0
        try:
            cart_items = CartItem.objects.filter(cart=cart, is_active=True, product__is_sold=False)
        except CartItem.DoesNotExist:
            cart_items = None
    total_without_tax = 0
    for item in cart_items:
        total_without_tax += item.product.price
    tax = round(total_without_tax / 100 * 15, 2)
    if total_without_tax >= 150:
        delivery = 0
    else:
        delivery = 15
    total_with_tax_and_shipping_without_bonuses = total_without_tax + tax + delivery
    if total_with_tax_and_shipping_without_bonuses / 2 < bonus_points:
        bonus_points = total_with_tax_and_shipping_without_bonuses // 2
    total_with_tax_and_shipping = round(total_without_tax + tax + delivery - bonus_points, 2)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            if request.user.is_authenticated:
                data.user = request.user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.email = form.cleaned_data['email']
            data.receiver_phone = form.cleaned_data['receiver_phone']
            data.sender_phone = form.cleaned_data['sender_phone']
            data.order_note = form.cleaned_data.get('order_note')
            data.city = form.cleaned_data['city']
            data.postal = form.cleaned_data['postal']
            data.address = form.cleaned_data['address']
            data.apartment = form.cleaned_data.get('apartment')
            data.wants_emails = form.cleaned_data['wants_emails']
            data.order_total = total_with_tax_and_shipping
            data.status = 'New'
            data.tax = tax
            data.delivery = delivery
            data.bonus_points_used = bonus_points
            data.total_without_tax = total_without_tax
            data.save()

            # generate order number
            yr = int(datetime.date.today().year)
            dt = int(datetime.date.today().day)
            mt = int(datetime.date.today().month)
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            return redirect(reverse('place_order', kwargs={'order_number': order_number}))
    else:
        form = OrderForm()
    context = {
        'form': form,
        'total_without_tax': total_without_tax,
        'tax': tax,
        'delivery': delivery,
        'total': total_with_tax_and_shipping,
        'bonus_points': bonus_points,
    }
    return render(request, 'carts/checkout.html', context)


def single_product_checkout(request, product_id):
    product = Product.objects.get(id=product_id)
    total_without_tax = product.price
    tax = round(total_without_tax / 100 * 15, 2)
    if total_without_tax >= 150:
        delivery = 0
    else:
        delivery = 15
    if request.user.is_authenticated:
        users_account = Account.objects.get(email=request.user.email)
        bonus_points = users_account.bonus_points
    else:
        bonus_points = 0
    total_with_tax_and_shipping_without_bonuses = total_without_tax + tax + delivery
    if total_with_tax_and_shipping_without_bonuses / 2 < bonus_points:
        bonus_points = total_with_tax_and_shipping_without_bonuses // 2
    total_with_tax_and_shipping = round(total_without_tax + tax + delivery - bonus_points, 2)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            if request.user.is_authenticated:
                data.user = request.user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.email = form.cleaned_data['email']
            data.receiver_phone = form.cleaned_data['receiver_phone']
            data.sender_phone = form.cleaned_data['sender_phone']
            data.order_note = form.cleaned_data.get('order_note')
            data.city = form.cleaned_data['city']
            data.postal = form.cleaned_data['postal']
            data.address = form.cleaned_data['address']
            data.apartment = form.cleaned_data.get('apartment')
            data.wants_emails = form.cleaned_data['wants_emails']
            data.order_total = total_with_tax_and_shipping
            data.status = 'New'
            data.tax = tax
            data.delivery = delivery
            data.total_without_tax = total_without_tax
            data.bonus_points_used = bonus_points
            data.save()

            # generate order number
            yr = int(datetime.date.today().year)
            dt = int(datetime.date.today().day)
            mt = int(datetime.date.today().month)
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            return redirect(reverse('place_order', kwargs={
                'order_number': order_number,
                'product_id': product_id,
            }))
    else:
        form = OrderForm()
    context = {
        'form': form,
        'total_without_tax': total_without_tax,
        'tax': tax,
        'delivery': delivery,
        'total': total_with_tax_and_shipping,
        'product': product,
        'bonus_points': bonus_points,
    }
    return render(request, 'carts/single_product_checkout.html', context)
