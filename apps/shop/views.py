from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import OperationalError, ProgrammingError
from .models import (
    Product,
    BannerSlide,
    HomeSettings,
    Category,
    ProductReview,
    Order,
    OrderItem,
)


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
    # نمایش همه محصولات فعال (نه فقط ویژه)
    featured_products = safe_queryset(
        Product.objects.filter(is_active=True).order_by("-created_at")[:6]
    )
    banners = safe_queryset(
        BannerSlide.objects.filter(is_active=True).order_by("order")
    )
    settings = get_settings()

    for product in featured_products:
        product.formatted_price = f"{product.price:,}"

    context = {
        "featured_products": featured_products,
        "banners": banners,
        "settings": settings,
        "products": featured_products,
    }
    return render(request, "shop/index.html", context)


def user_has_bought_product(user, product):
    """بررسی اینکه کاربر محصول را قبلاً خریده باشد."""
    if not user or not user.is_authenticated:
        return False
    return OrderItem.objects.filter(
        product=product,
        order__user=user,
        order__status__in=["paid", "processing", "shipped", "delivered", "pending"],
    ).exists()


def product_detail(request, product_slug):
    """صفحه جزئیات محصول"""
    try:
        product = get_object_or_404(Product, slug=product_slug, is_active=True)
        product.formatted_price = f"{product.price:,}"

        if request.method == "POST" and "rating" in request.POST:
            if not request.user.is_authenticated:
                messages.error(request, "برای ثبت دیدگاه، ابتدا وارد حساب خود شوید.")
                return redirect("accounts:login")

            if not user_has_bought_product(request.user, product):
                messages.error(
                    request,
                    "فقط کاربران ثبت‌نام‌شده‌ای که این محصول را خریداری کرده‌اند می‌توانند دیدگاه ثبت کنند.",
                )
                return redirect(product.get_absolute_url())

            try:
                rating = int(request.POST.get("rating", 0))
                if rating < 1 or rating > 5:
                    raise ValueError
            except (TypeError, ValueError):
                messages.error(request, "امتیاز وارد شده نامعتبر است.")
                return redirect(product.get_absolute_url())

            comment = (request.POST.get("comment") or "").strip()
            ProductReview.objects.update_or_create(
                product=product,
                user=request.user,
                defaults={"rating": rating, "comment": comment},
            )
            messages.success(request, "دیدگاه شما با موفقیت ثبت شد.")
            return redirect(product.get_absolute_url())

        similar_products = []
        for similar_item in product.similar_products.all():
            similar = similar_item.similar
            similar.formatted_price = f"{similar.price:,}"
            similar_products.append(similar)

        if not similar_products and product.category:
            similar_products = Product.objects.filter(
                category=product.category, is_active=True
            ).exclude(id=product.id)[:3]
            for similar in similar_products:
                similar.formatted_price = f"{similar.price:,}"

        reviews = product.reviews.select_related("user").all()
        average_rating = 0
        if reviews:
            average_rating = round(
                sum(item.rating for item in reviews) / len(reviews), 1
            )
        user_review = None
        if request.user.is_authenticated:
            user_review = product.reviews.filter(user=request.user).first()

        has_bought_product = user_has_bought_product(request.user, product)
    except (OperationalError, ProgrammingError):
        from django.http import Http404

        raise Http404("محصول مورد نظر یافت نشد")

    context = {
        "product": product,
        "similar_products": similar_products,
        "reviews": reviews,
        "average_rating": average_rating,
        "user_review": user_review,
        "has_bought_product": has_bought_product,
        "can_submit_review": request.user.is_authenticated and has_bought_product,
    }
    return render(request, "shop/product_detail.html", context)


def product_list(request):
    """صفحه لیست تمام محصولات"""
    products_list = safe_queryset(
        Product.objects.filter(is_active=True).order_by("-created_at")
    )

    for product in products_list:
        product.formatted_price = f"{product.price:,}"

    category_slug = request.GET.get("category")
    if category_slug:
        products_list = [
            p for p in products_list if p.category and p.category.slug == category_slug
        ]

    sort = request.GET.get("sort", "newest")
    if sort == "price-asc":
        products_list = sorted(products_list, key=lambda x: x.price)
    elif sort == "price-desc":
        products_list = sorted(products_list, key=lambda x: x.price, reverse=True)
    elif sort == "title":
        products_list = sorted(products_list, key=lambda x: x.title)

    paginator = Paginator(products_list, 12)
    page = request.GET.get("page")
    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    categories = safe_queryset(Category.objects.filter(is_active=True))

    context = {
        "products": products,
        "categories": categories,
    }
    return render(request, "shop/products.html", context)


def admin_dashboard(request):
    """داشبورد مدیریت"""
    if not request.user.is_superuser:
        from django.http import Http404

        raise Http404("صفحه مورد نظر یافت نشد")
    return render(request, "shop/admin_dashboard.html")


def about(request):
    """صفحه درباره ما"""
    return render(request, "shop/about.html")
