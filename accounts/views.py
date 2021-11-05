import django.urls.exceptions
from django.shortcuts import render, redirect, reverse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from accounts.models import Account
from .forms import RegistrationForm, EditProfile
from django.contrib import auth, messages
from carts.models import Cart, CartItem
from carts.views import _cart_id
from orders.models import Order


# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            phone_number = form.cleaned_data['phone_number']
            password = form.cleaned_data['password']
            wants_emails = form.cleaned_data['wants_emails']
            user = Account.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                email=email,
                phone_number=phone_number,
                wants_emails=wants_emails,
                password=password,
            )
            user.save()
            messages.success(request, 'Your account has been created. Please, log in.')
            redirect_url = request.META['HTTP_REFERER'].split('=')[-1]
            try:
                return redirect(reverse(redirect_url))
            except django.urls.exceptions.NoReverseMatch:
                return redirect(reverse('login'))
    else:
        form = RegistrationForm()
    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)


def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = auth.authenticate(email=email, password=password)

        if user:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items_exist = CartItem.objects.filter(cart=cart).exists()
            if cart_items_exist:
                users_cart_items = CartItem.objects.filter(user=user)
                print(users_cart_items)
                cart_items = CartItem.objects.filter(cart=cart)
                if not users_cart_items:
                    for cart_item in cart_items:
                        cart_item.user = user
                        cart_item.save()
                else:
                    for cart_item in cart_items:
                        if not users_cart_items.filter(product__id=cart_item.product.id).exists():
                            cart_item.user = user
                            cart_item.save()
                        else:
                            pass
            auth.login(request, user)
            redirect_url = request.META['HTTP_REFERER'].split('=')[-1]
            try:
                return redirect(reverse(redirect_url))
            except django.urls.exceptions.NoReverseMatch:
                return redirect(reverse('home'))
        else:
            messages.error(request, 'No account matched the credentials provided')
            return redirect(request.META['HTTP_REFERER'])
    return render(request, 'accounts/login.html')


@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    if request.GET.get('next'):
        try:
            return redirect(reverse(request.GET['next']))
        except django.urls.exceptions.NoReverseMatch:
            return redirect('home')
    else:
        return redirect('home')


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if Account.objects.filter(email__exact=email).exists():
            user = Account.objects.get(email__exact=email)

            site = get_current_site(request)
            mail_subject = 'Password reset'
            message = render_to_string('accounts/forgot_password_email.html', {
                'user': user,
                'domain': site,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user)
            })
            to_email = email
            send_email = EmailMessage(mail_subject, message, to=[to_email])
            send_email.send(fail_silently=False)

            messages.success(request,
                             'Password reset email has been sent to your email address. '
                             'Make sure to check the "spam" folder')
            return redirect(reverse('login'))

        else:
            messages.error(request, 'Account does not exist')
            return redirect(reverse('forgot_password'))
    return render(request, 'accounts/forgot_password.html')


def reset_password_validate(request, uidb64, token):
    uid = urlsafe_base64_decode(uidb64).decode()
    try:
        user = Account._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, Account.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        request.session['uid'] = uid
        messages.success(request, 'Create a new password')
        return redirect(reverse('reset_password'))
    else:
        messages.error(request, 'Reset link has been expired')
        return redirect(reverse('login'))


def reset_password(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords did not match')
            return redirect(reverse('reset_password'))
        else:
            uid = request.session.get('uid')
            user = Account.objects.get(pk=uid)
            user.set_password(password)
            user.save()
            messages.success(request, 'Password has been successfully changed')
            return redirect(reverse('login'))
    else:
        return render(request, 'accounts/reset_password.html')


@login_required(login_url='login')
def dashboard(request):
    orders = Order.objects.filter(user__id=request.user.id, status__in=('Paid', 'Delivered')).order_by(
        '-order_number')
    account = Account.objects.get(id=request.user.id)
    total_spent = 0
    bonuses_earned = 0
    for order in orders:
        total_spent += order.order_total
        bonuses_earned += order.total_without_tax // 10
    context = {
        'orders': orders,
        'account': account,
        'total_spent': total_spent,
        'bonuses_earned': bonuses_earned
    }
    return render(request, 'accounts/dashboard.html', context)


@login_required(login_url='login')
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfile(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated')
            return redirect(reverse('edit_profile'))
    else:
        form = EditProfile(instance=request.user)
    context = {
        'form': form,
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required(login_url='login')
def change_password(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        current_user = Account.objects.get(email=request.user.email)

        if current_user.check_password(current_password):
            if new_password == confirm_password:
                current_user.set_password(new_password)
                current_user.save()
                auth.logout(request)
                messages.success(request, 'Password has been updated. Please, log in again.')
                return redirect(reverse('change_password'))
            else:
                messages.warning(request, 'New passwords do not match')
                return redirect(reverse('change_password'))
        else:
            messages.warning(request, 'Your current password is not correct')
            return redirect(reverse('change_password'))
    return render(request, 'accounts/change_password.html')
