from django.shortcuts import render, redirect, reverse
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from .models import Order, Payment, OrderProduct
from .forms import TrackOrderForm
from products.models import Product
from carts.models import Cart, CartItem
from accounts.models import Account
from carts.views import _cart_id
from django.contrib import messages
import json


# Create your views here.
def payments(request, product_id=None):
    body = json.loads(request.body)
    order = Order.objects.get(order_number=body['orderID'])
    # Transaction details to database
    payment = Payment(
        payment_id=body['transID'],
        status=body['status'],
        amount_paid=order.order_total,
    )
    payment.save()
    order.status = "Paid"
    order.payment = Payment.objects.get(payment_id=body['transID'])
    order.save()

    if request.user.is_authenticated:
        user_account = Account.objects.get(email=request.user.email)
        user_account.bonus_points -= order.bonus_points_used
        user_account.save()
        user_account.bonus_points += order.total_without_tax // 10
        user_account.save()

    if not product_id:
        # Get cart items and move them to order products
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart)
        for item in cart_items:
            order_product = OrderProduct()
            order_product.order = order
            order_product.payment = payment
            order_product.product_id = item.product_id
            order_product.product_price = item.product.price
            order_product.save()

            # increase the 'times purchased' in the product model and set 'is_sold' to True
            product = Product.objects.get(id=order_product.product_id)
            product.times_purchased += 1
            product.is_sold = True
            product.save()

        # Clear the cart
        cart_items.delete()

    else:
        product = Product.objects.get(id=product_id)
        order_product = OrderProduct()
        order_product.order = order
        order_product.payment = payment
        order_product.product_id = product_id
        order_product.product_price = product.price
        order_product.save()

        # increase the 'times purchased' in the product model and set 'is_sold' to True
        product.times_purchased += 1
        product.is_sold = True
        product.save()

    # send email if successful payment
    domain = get_current_site(request)

    mail_subject = "Ontario Flowers Purchase Details"
    message = render_to_string('emails/successful_payment_mail_to_customer.html', {
        'order': order,
        'domain': domain,
    })
    to_email = order.email
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    # send email to Carolina to notify about the purchase
    mail_subject = "Ontario Flowers New Purchase!"
    message = render_to_string('emails/successful_payment_mail_to_company.html', {
        'order': order,
        'domain': domain,
    })
    to_email = 'illymarev@gmail.com'
    send_email = EmailMessage(mail_subject, message, to=[to_email])
    send_email.send()

    return render(request, 'orders/payments.html')


def place_order(request, order_number, product_id=None):
    order = Order.objects.get(order_number=order_number)
    context = {
        'order': order,
        'product_id': product_id
    }
    return render(request, 'orders/payments.html', context)


def order_complete(request):
    return render(request, 'orders/order_complete.html')


def track_order(request):
    if request.method == "POST":
        form = TrackOrderForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            order_number = form.cleaned_data['order_number']
            if Order.objects.filter(email=email, order_number=order_number).exists():
                return redirect(reverse('order_details', kwargs={'email': email, 'order_number': order_number}))
            else:
                messages.warning(request, 'No orders matched your input data')
    form = TrackOrderForm()
    context = {
        'form': form
    }
    return render(request, 'orders/track_order.html', context)


def order_details(request, email, order_number):
    try:
        order = Order.objects.get(email=email, order_number=order_number)
        order_products = OrderProduct.objects.filter(order_id=order.id)
    except Order.DoesNotExist:
        order = None
        order_products = None
    context = {
        'order': order,
        'order_products': order_products,
    }
    return render(request, 'orders/order_details.html', context)
