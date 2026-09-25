# apps/accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.db import IntegrityError
from .forms import RegisterForm, LoginForm, EditProfileForm
from .models import Profile
from apps.shop.models import Cart
from apps.shop.models import Order


@login_required
def dashboard_view(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(
            user=request.user, phone="", avatar="figmax-pfp1.png"
        )

    orders = Order.objects.filter(user=request.user)
    cart = Cart.objects.filter(user=request.user).first()
    cart_items = cart.items.all() if cart else []

    context = {
        "orders": orders,
        "cart_items": cart_items,
        "orders_count": orders.count(),
        "cart_count": sum(item.quantity for item in cart_items),
        "total_spent": sum(order.total_price for order in orders),
        "profile": profile,
    }
    return render(request, "accounts/dashboard.html", context)


@login_required
def orders_view(request):
    orders = Order.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "accounts/my_order.html", {"orders": orders})


@login_required
def cart_view(request):
    cart = Cart.objects.filter(user=request.user).first()
    cart_items = cart.items.all() if cart else []
    total = cart.get_total_price() if cart else 0
    return render(request, "shop/cart.html", {"cart_items": cart_items, "total": total})


@login_required
def edit_profile_view(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user, phone="")

    if request.method == "POST":
        form = EditProfileForm(request.POST)
        if form.is_valid():
            user = request.user
            user.first_name = form.cleaned_data["first_name"]
            user.last_name = form.cleaned_data["last_name"]
            user.email = form.cleaned_data["email"]
            user.save()

            if form.cleaned_data["phone"]:
                # بررسی تکراری نبودن شماره تلفن
                if (
                    Profile.objects.filter(phone=form.cleaned_data["phone"])
                    .exclude(user=user)
                    .exists()
                ):
                    messages.error(request, "❌ این شماره تلفن قبلاً ثبت شده است!")
                    return render(
                        request,
                        "accounts/profile.html",
                        {"form": form, "profile": profile},
                    )
                profile.phone = form.cleaned_data["phone"]
                profile.save()

            if form.cleaned_data["new_password"]:
                user.set_password(form.cleaned_data["new_password"])
                user.save()
                login(request, user)

            messages.success(request, "✅ پروفایل با موفقیت بروزرسانی شد!")
            return redirect("accounts:edit_profile")
    else:
        form = EditProfileForm(
            initial={
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "email": request.user.email,
                "phone": profile.phone,
            }
        )

    return render(request, "accounts/profile.html", {"form": form, "profile": profile})


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)

        # ===== اعتبارسنجی اضافی =====
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip()
        phone = request.POST.get("phone", "").strip()

        errors = []

        # بررسی نام کاربری تکراری
        from django.contrib.auth.models import User

        if User.objects.filter(username=username).exists():
            errors.append("❌ این نام کاربری قبلاً ثبت شده است!")

        # بررسی ایمیل تکراری
        if email and User.objects.filter(email=email).exists():
            errors.append("❌ این ایمیل قبلاً ثبت شده است!")

        # بررسی شماره تلفن تکراری
        if phone and Profile.objects.filter(phone=phone).exists():
            errors.append("❌ این شماره تلفن قبلاً ثبت شده است!")

        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, "accounts/register.html", {"form": form})

        if form.is_valid():
            try:
                user = form.save()
                import random

                avatar = f"figmax-pfp{random.randint(1, 7)}.png"
                Profile.objects.create(
                    user=user, phone=form.cleaned_data["phone"], avatar=avatar
                )
                login(request, user)
                messages.success(request, "✅ ثبت‌نام با موفقیت انجام شد! خوش آمدید 🎉")
                return redirect("accounts:dashboard")
            except IntegrityError as e:
                if "phone" in str(e):
                    messages.error(request, "❌ این شماره تلفن قبلاً ثبت شده است!")
                else:
                    messages.error(
                        request, "❌ خطا در ثبت نام! لطفاً دوباره تلاش کنید."
                    )
                return render(request, "accounts/register.html", {"form": form})
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST, request=request)
        if form.is_valid():
            user = form.cleaned_data["user"]
            remember_me = form.cleaned_data.get("remember_me")
            login(request, user)
            if not remember_me:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(1209600)  # 2 هفته
            messages.success(request, f"👋 خوش آمدید {user.username}!")
            return redirect("accounts:dashboard")
    else:
        form = LoginForm(request=request)
    return render(request, "accounts/login.html", {"form": form})


def logout_view(request):
    logout(request)
    messages.info(request, "👋 با موفقیت خارج شدید!")
    return redirect("shop:index")
