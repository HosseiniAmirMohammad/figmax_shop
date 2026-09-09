from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import OperationalError, ProgrammingError
from .models import Product, BannerSlide, HomeSettings, Category


def safe_queryset(queryset, default_empty=True):
    """安全地执行查询，如果数据库不可用则返回空列表"""
    try:
        return list(queryset)
    except (OperationalError, ProgrammingError):
        return [] if default_empty else None


def get_settings():
    """دریافت تنظیمات سایت با پشتیبانی از حالت بدون دیتابیس"""
    try:
        settings = HomeSettings.objects.first()
        if not settings:
            settings = HomeSettings.objects.create()
        return settings
    except (OperationalError, ProgrammingError):
        return None


def index(request):
    """صفحه اصلی فروشگاه"""
    featured_products = safe_queryset(
        Product.objects.filter(is_active=True, is_featured=True)[:6]
    )
    banners = safe_queryset(
        BannerSlide.objects.filter(is_active=True).order_by('order')
    )
    settings = get_settings()
    
    for product in featured_products:
        product.formatted_price = f"{product.price:,}"
    
    context = {
        'featured_products': featured_products,
        'banners': banners,
        'settings': settings,
        'products': featured_products,
    }
    return render(request, 'shop/index.html', context)


def product_detail(request, product_slug):
    """صفحه جزئیات محصول"""
    try:
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
    except (OperationalError, ProgrammingError):
        from django.http import Http404
        raise Http404("محصول مورد نظر یافت نشد")
    
    context = {
        'product': product,
        'similar_products': similar_products,
    }
    return render(request, 'shop/product_detail.html', context)


def product_list(request):
    """صفحه لیست تمام محصولات"""
    products_list = safe_queryset(
        Product.objects.filter(is_active=True).order_by('-created_at')
    )
    
    for product in products_list:
        product.formatted_price = f"{product.price:,}"
    
    category_slug = request.GET.get('category')
    if category_slug:
        products_list = [p for p in products_list if p.category and p.category.slug == category_slug]
    
    sort = request.GET.get('sort', 'newest')
    if sort == 'price-asc':
        products_list = sorted(products_list, key=lambda x: x.price)
    elif sort == 'price-desc':
        products_list = sorted(products_list, key=lambda x: x.price, reverse=True)
    elif sort == 'title':
        products_list = sorted(products_list, key=lambda x: x.title)
    
    paginator = Paginator(products_list, 12)
    page = request.GET.get('page')
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)
    
    categories = safe_queryset(
        Category.objects.filter(is_active=True)
    )
    
    context = {
        'products': products,
        'categories': categories,
    }
    return render(request, 'shop/products.html', context)


def admin_dashboard(request):
    """داشبورد مدیریت"""
    if not request.user.is_superuser:
        from django.http import Http404
        raise Http404("صفحه مورد نظر یافت نشد")
    return render(request, 'shop/admin_dashboard.html')


def about(request):
    """صفحه درباره ما"""
    return render(request, 'shop/about.html')