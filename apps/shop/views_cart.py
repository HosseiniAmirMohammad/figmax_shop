from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.exceptions import ValidationError
from django_ratelimit.decorators import ratelimit
from .models import Cart, CartItem, Product, Order, OrderItem


def get_or_create_cart(request):
    """دریافت یا ساخت سبد خرید برای کاربر یا نشست"""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart


def format_price(price):
    """فرمت قیمت با کاما - مثال: 1500000 → 1,500,000"""
    try:
        return f"{int(price):,}"
    except (ValueError, TypeError):
        return str(price)


@ratelimit(key='ip', rate='10/m', method='POST')
def add_to_cart(request):
    """
    افزودن محصول به سبد خرید
    محدودیت: هر آیپی ۱۰ بار در دقیقه
    """
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        
        if not product_id:
            messages.error(request, 'شناسه محصول وارد نشده است!')
            return redirect('shop:product_list')
        
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity < 1:
                messages.error(request, 'تعداد باید حداقل ۱ باشد!')
                return redirect(request.META.get('HTTP_REFERER', 'shop:product_list'))
        except ValueError:
            messages.error(request, 'تعداد نامعتبر است!')
            return redirect(request.META.get('HTTP_REFERER', 'shop:product_list'))
        
        product = get_object_or_404(Product, id=product_id, is_active=True)
        
        # بررسی موجودی
        if quantity > product.stock:
            messages.error(request, f'موجودی کافی نیست! فقط {product.stock} عدد موجود است.')
            return redirect(request.META.get('HTTP_REFERER', 'shop:product_list'))
        
        cart = get_or_create_cart(request)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )
        
        if not created:
            if cart_item.quantity + quantity <= product.stock:
                cart_item.quantity += quantity
                cart_item.save()
            else:
                messages.error(request, f'موجودی کافی نیست! فقط {product.stock} عدد موجود است.')
                return redirect(request.META.get('HTTP_REFERER', 'shop:product_list'))
        
        messages.success(request, f'✅ {product.title} به سبد خرید اضافه شد!')
        return redirect('shop:cart')
    
    return redirect('shop:product_list')


def cart_view(request):
    cart = get_or_create_cart(request)
    cart_items = cart.items.select_related('product').all()
    
    total_price = cart.get_total_price()
    
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'shop/cart.html', context)


def update_cart_item(request, item_id):
    """به‌روزرسانی تعداد آیتم سبد خرید"""
    if request.method == 'POST':
        try:
            quantity = int(request.POST.get('quantity', 1))
            if quantity < 0:
                return JsonResponse({'error': 'تعداد نامعتبر است!'}, status=400)
        except ValueError:
            return JsonResponse({'error': 'تعداد نامعتبر است!'}, status=400)
        
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
        
        # اگر تعداد صفر یا منفی بود، حذف کن
        if quantity <= 0:
            cart_item.delete()
            return JsonResponse({
                'success': True,
                'total_items': cart.get_total_items(),
                'total_price': format_price(cart.get_total_price()),
                'message': 'آیتم از سبد خرید حذف شد!'
            })
        
        # بررسی موجودی
        if quantity > cart_item.product.stock:
            return JsonResponse({'error': f'موجودی کافی نیست! فقط {cart_item.product.stock} عدد موجود است.'}, status=400)
        
        cart_item.quantity = quantity
        cart_item.save()
        
        return JsonResponse({
            'success': True,
            'total_items': cart.get_total_items(),
            'total_price': format_price(cart.get_total_price()),
            'message': 'تعداد آیتم به‌روزرسانی شد!'
        })
    
    return JsonResponse({'error': 'درخواست نامعتبر است!'}, status=400)


def remove_from_cart(request, item_id):
    """حذف آیتم از سبد خرید"""
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    cart_item.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'total_items': cart.get_total_items(),
            'total_price': format_price(cart.get_total_price()),
            'message': 'آیتم از سبد خرید حذف شد!'
        })
    
    messages.success(request, '🗑️ آیتم از سبد خرید حذف شد!')
    return redirect('shop:cart')


def cart_count(request):
    """دریافت تعداد آیتم‌های سبد خرید (برای AJAX)"""
    cart = get_or_create_cart(request)
    return JsonResponse({'count': cart.get_total_items()})


@login_required
def checkout(request):
    """ثبت نهایی سفارش"""
    cart = get_or_create_cart(request)
    items = cart.items.select_related('product').all()
    
    if not items:
        messages.error(request, 'سبد خرید شما خالی است!')
        return redirect('shop:cart')
    
    # فرمت قیمت برای آیتم‌ها
    for item in items:
        item.product.formatted_price = format_price(item.product.price)
    
    total_price = cart.get_total_price()
    formatted_total = format_price(total_price)
    
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        full_name = f"{first_name} {last_name}".strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        address = request.POST.get('address', '').strip()
        postal_code = request.POST.get('postal_code', '').strip()
        
        # اعتبارسنجی فیلدها
        errors = []
        if not first_name:
            errors.append('نام')
        if not last_name:
            errors.append('نام خانوادگی')
        if not phone:
            errors.append('شماره تماس')
        if not address:
            errors.append('آدرس')
        
        if errors:
            messages.error(request, f'لطفاً فیلدهای زیر را پر کنید: {", ".join(errors)}')
            return render(request, 'shop/checkout.html', {
                'items': items, 
                'total_price': total_price,
                'formatted_total': formatted_total,
            })
        
        # اعتبارسنجی شماره تلفن
        if not phone.isdigit() or len(phone) < 10:
            messages.error(request, 'شماره تلفن معتبر نیست!')
            return render(request, 'shop/checkout.html', {
                'items': items, 
                'total_price': total_price,
                'formatted_total': formatted_total,
            })
        
        with transaction.atomic():
            # ایجاد سفارش
            order = Order.objects.create(
                user=request.user,
                total_price=total_price,
                full_name=full_name,
                phone=phone,
                address=address,
                postal_code=postal_code,
                status='pending'
            )
            
            # ایجاد آیتم‌های سفارش و کاهش موجودی
            for cart_item in items:
                OrderItem.objects.create(
                    order=order,
                    product=cart_item.product,
                    quantity=cart_item.quantity,
                    price=cart_item.product.price
                )
                
                product = cart_item.product
                product.stock -= cart_item.quantity
                product.save()
            
            # خالی کردن سبد خرید
            items.delete()
        
        messages.success(request, f'✅ سفارش شما با موفقیت ثبت شد! شماره سفارش: #{order.order_number}')
        return redirect('shop:order_detail', order_id=order.id)
    
    context = {
        'items': items,
        'total_price': total_price,
        'formatted_total': formatted_total,
    }
    return render(request, 'shop/checkout.html', context)


@login_required
def orders_list(request):
    """لیست سفارشات کاربر"""
    orders = Order.objects.filter(user=request.user).select_related('user').order_by('-created_at')
    context = {
        'orders': orders,
    }
    return render(request, 'shop/orders.html', context)


@login_required
def order_detail(request, order_id):
    """نمایش جزئیات یک سفارش"""
    order = get_object_or_404(
        Order.objects.select_related('user').prefetch_related('shop_items__product'), 
        id=order_id, 
        user=request.user
    )
    context = {
        'order': order,
    }
    return render(request, 'shop/order_detail.html', context)