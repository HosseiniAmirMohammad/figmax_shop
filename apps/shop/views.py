from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, BannerSlide, HomeSettings, Category


def index(request):
    products = Product.objects.filter(is_active=True)
    featured_products = products.filter(is_featured=True)[:6]
    banners = BannerSlide.objects.filter(is_active=True).order_by('order')
    settings = HomeSettings.objects.first()
    
    if not settings:
        settings = HomeSettings.objects.create()
    
    for product in featured_products:
        product.formatted_price = f"{product.price:,}"
    
    context = {
        'featured_products': featured_products,
        'banners': banners,
        'settings': settings,
        'products': products,
    }
    return render(request, 'shop/index.html', context)


def product_detail(request, product_slug):
    product = get_object_or_404(Product, slug=product_slug, is_active=True)
    product.formatted_price = f"{product.price:,}"
    
    similar_products = []
    for similar_item in product.similar_products.all():
        similar = similar_item.similar
        similar.formatted_price = f"{similar.price:,}"
        similar_products.append(similar)
    
    if not similar_products and product.category:
        similar_products = Product.objects.filter(
            category=product.category, 
            is_active=True
        ).exclude(id=product.id)[:3]
        for similar in similar_products:
            similar.formatted_price = f"{similar.price:,}"
    
    context = {
        'product': product,
        'similar_products': similar_products,
    }
    return render(request, 'shop/product_detail.html', context)


def product_list(request):
    """صفحه لیست تمام محصولات"""
    products_list = Product.objects.filter(is_active=True)
    
    for product in products_list:
        product.formatted_price = f"{product.price:,}"
    
    category_slug = request.GET.get('category')
    if category_slug:
        products_list = products_list.filter(category__slug=category_slug)
    
    sort = request.GET.get('sort', 'newest')
    if sort == 'price-asc':
        products_list = products_list.order_by('price')
    elif sort == 'price-desc':
        products_list = products_list.order_by('-price')
    elif sort == 'title':
        products_list = products_list.order_by('title')
    else:
        products_list = products_list.order_by('-created_at')
    
    paginator = Paginator(products_list, 12)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    # فرمت قیمت برای محصولات صفحه‌بندی شده
    for product in products:
        product.formatted_price = f"{product.price:,}"
    
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'shop/products.html', context)


def admin_dashboard(request):
    if not request.user.is_superuser:
        from django.http import Http404
        raise Http404("صفحه مورد نظر یافت نشد")
    return render(request, 'shop/admin_dashboard.html')


def about(request):
    return render(request, 'shop/about.html')