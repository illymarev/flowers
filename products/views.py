from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from .models import Product, SingleFlower, ReviewRating
from .forms import ReviewForm
from carts.models import CartItem, Cart
from carts.views import _cart_id
from categories.models import Category


# Create your views here.

def flower_list(request, category_slug=None):
    if request.GET.get('flowers'):
        # get all single_flowers to filter the queryset
        criteria = request.GET.getlist('flowers')
    else:
        criteria = None

    if request.GET.get('sort'):
        # get sort method to order the queryset
        order_value = request.GET.get('sort')
        if order_value == 'l2h':
            order_param = 'price'
        elif order_value == 'h2l':
            order_param = '-price'
        elif order_value == 'popularity':
            order_param = '-times_purchased'
        else:
            order_param = '-created'
    else:
        order_param = '-created'
    if category_slug:
        # get the category object and filter flowers by this category
        category = get_object_or_404(Category, is_plant=False, slug=category_slug)
        flowers = Product.objects.filter(is_plant=False, category=category).order_by('is_sold', order_param)
        if criteria:
            for i in criteria:
                # Filter many times to get objects which match all single flowers
                flowers = flowers.filter(flowers_inside=i).order_by('is_sold', order_param)
    else:
        flowers = Product.objects.filter(is_plant=False).order_by('is_sold', order_param)
        if criteria:
            for i in criteria:
                # Filter many times to get objects which match all single flowers
                flowers = flowers.filter(flowers_inside=i).order_by('is_sold', order_param)

    paginator = Paginator(flowers, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    single_flowers = SingleFlower.objects.all().order_by('name')
    context = {
        'page_obj': page_obj,
        'single_flowers': single_flowers,
    }
    return render(request, 'products/flower_list.html', context)


def plant_list(request, category_slug=None):
    if request.GET.get('sort'):
        order_value = request.GET.get('sort')
        if order_value == 'l2h':
            order_param = 'price'
        elif order_value == 'h2l':
            order_param = '-price'
        elif order_value == 'popularity':
            order_param = '-times_purchased'
        else:
            order_param = '-created'
    else:
        order_param = '-created'
    if category_slug:
        # get the category object and filter flowers by this category
        category = get_object_or_404(Category, is_plant=True, slug=category_slug)
        plants = Product.objects.filter(is_plant=True, category=category).order_by('is_sold', order_param)
    else:
        plants = Product.objects.filter(is_plant=True).order_by('is_sold', order_param)

    paginator = Paginator(plants, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'products/plant_list.html', context)


def product_details(request, id):
    product = Product.objects.get(id=id)
    single_flowers = SingleFlower.objects.filter(product__id=product.id).order_by('name')
    cart = Cart.objects.get(cart_id=_cart_id(request))
    reviews = ReviewRating.objects.filter(product__id=id).order_by('-created_at')
    if request.user.is_authenticated:
        in_cart = CartItem.objects.filter(product__id=product.id, user=request.user).exists()
    else:
        in_cart = CartItem.objects.filter(product__id=product.id, cart_id=cart).exists()
    context = {
        'product': product,
        'single_flowers': single_flowers,
        'in_cart': in_cart,
        'reviews': reviews,
    }
    return render(request, 'products/product_details.html', context)


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            review = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST,
                              instance=review)  # instance is specified to update if review already exists)
            form.save()
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.product_id = product_id
                if request.user.is_authenticated:
                    data.user_id = request.user.id
                data.display_name = form.cleaned_data['display_name']
                if not data.display_name:
                    data.display_name = 'Anonymous'
                data.save()
                return redirect(url)
