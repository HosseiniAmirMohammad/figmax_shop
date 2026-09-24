from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
import os
import random
import string
from django.utils import timezone


# اعتبارسنجی تصاویر (امنیت)
def validate_image_size(value):
    """اعتبارسنجی سایز تصویر (حداکثر 5 مگابایت)"""
    if value.size > 5 * 1024 * 1024:
        raise ValidationError("حجم تصویر نباید بیشتر از 5 مگابایت باشد!")


def validate_image_extension(value):
    """اعتبارسنجی پسوند تصویر"""
    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
    if ext not in valid_extensions:
        raise ValidationError("پسوند تصویر مجاز نیست! (فقط: jpg, jpeg, png, gif, webp)")


def validate_image_dimensions(value):
    """اعتبارسنجی ابعاد تصویر (اختیاری)"""
    try:
        from PIL import Image

        img = Image.open(value)
        width, height = img.size
        if width < 200 or height < 200:
            raise ValidationError("ابعاد تصویر باید حداقل 200x200 پیکسل باشد!")
    except ImportError:
        pass


class Category(models.Model):
    name = models.CharField("نام دسته", max_length=100)
    slug = models.SlugField("اسلاگ", unique=True, allow_unicode=True)
    order = models.IntegerField("ترتیب", default=0)
    is_active = models.BooleanField("فعال", default=True)
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)

    class Meta:
        ordering = ["order", "name"]
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    title = models.CharField("عنوان محصول", max_length=200)
    slug = models.SlugField("اسلاگ", unique=True, allow_unicode=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="دسته‌بندی",
        related_name="products",
    )
    price = models.PositiveIntegerField("قیمت (تومان)")

    about_product = models.TextField(
        "درباره محصول",
        blank=True,
        help_text="توضیحات فنی، نحوه ساخت، جنس و مشخصات محصول",
    )
    character_story = models.TextField(
        "داستان شخصیت", blank=True, help_text="بیوگرافی و داستان شخصیت"
    )

    short_description = models.CharField("توضیحات کوتاه", max_length=300, blank=True)
    stock = models.PositiveIntegerField("موجودی", default=0)
    is_featured = models.BooleanField("محصول ویژه", default=False)
    is_active = models.BooleanField("فعال", default=True)
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین بروزرسانی", auto_now=True)

    banner_image = models.ImageField(
        "تصویر بنر محصول",
        upload_to="product_banners/",
        blank=True,
        null=True,
        validators=[validate_image_size, validate_image_extension],
        help_text="تصویر بنر بالای صفحه محصول (سایز پیشنهادی: 1200x400، حداکثر 5 مگابایت)",
    )
    banner_title = models.CharField("عنوان بنر", max_length=200, blank=True)
    banner_subtitle = models.CharField("زیرنویس بنر", max_length=300, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("shop:product_detail", args=[self.slug])

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class ProductImage(models.Model):
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="images", verbose_name="محصول"
    )
    image = models.ImageField(
        "تصویر",
        upload_to="products/",
        validators=[validate_image_size, validate_image_extension],
    )
    alt_text = models.CharField("متن جایگزین", max_length=100, blank=True)
    is_main = models.BooleanField("تصویر اصلی", default=False)
    order = models.IntegerField("ترتیب", default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "تصویر محصول"
        verbose_name_plural = "تصاویر محصول"

    def __str__(self):
        return f"{self.product.title} - تصویر {self.order + 1}"


class ProductSpecification(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="specifications",
        verbose_name="محصول",
    )
    key = models.CharField("عنوان مشخصه", max_length=100)
    value = models.CharField("مقدار مشخصه", max_length=200)
    order = models.IntegerField("ترتیب", default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "مشخصه محصول"
        verbose_name_plural = "مشخصات محصول"

    def __str__(self):
        return f"{self.key}: {self.value}"


class SimilarProduct(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="similar_products",
        verbose_name="محصول اصلی",
    )
    similar = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="similar_to",
        verbose_name="محصول مشابه",
    )
    order = models.IntegerField("ترتیب", default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "محصول مشابه"
        verbose_name_plural = "محصولات مشابه"
        unique_together = [["product", "similar"]]

    def __str__(self):
        return f"{self.product.title} ← {self.similar.title}"


class ProductReview(models.Model):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="محصول",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="product_reviews",
        verbose_name="کاربر",
    )
    rating = models.PositiveSmallIntegerField(
        "امتیاز",
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField("دیدگاه", blank=True)
    created_at = models.DateTimeField("تاریخ ثبت", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین بروزرسانی", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "دیدگاه محصول"
        verbose_name_plural = "دیدگاه‌های محصول"
        unique_together = [["product", "user"]]

    def __str__(self):
        return f"{self.user.username} - {self.product.title} ({self.rating} ستاره)"


class BannerSlide(models.Model):
    title = models.CharField(
        "عنوان", max_length=100, blank=True, null=True
    )  # ← اختیاری شد
    subtitle = models.CharField(
        "زیرنویس", max_length=200, blank=True, null=True
    )  # ← اختیاری شد
    image = models.ImageField(
        "تصویر",
        upload_to="banners/",
        validators=[validate_image_size, validate_image_extension],
    )
    link = models.CharField(
        "لینک", max_length=200, blank=True, help_text="مثلاً: /product/ghost-bust/"
    )
    order = models.IntegerField("ترتیب", default=0)
    is_active = models.BooleanField("فعال", default=True)
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "اسلاید بنر"
        verbose_name_plural = "اسلایدهای بنر"

    def __str__(self):
        return self.title or f"بنر {self.order + 1}"


class HomeSettings(models.Model):
    """تنظیمات صفحه اصلی - فقط یک نمونه از این مدل باید وجود داشته باشد"""

    # HERO SECTION
    hero_title = models.CharField(
        "عنوان اصلی هیرو", max_length=200, default="FIGMAX SHOP"
    )
    hero_subtitle = models.CharField(
        "زیرنویس هیرو",
        max_length=300,
        default="مجموعه‌ای از نفیس‌ترین فیگورهای کلکسیونی",
    )

    # COLORS
    hero_title_color = models.CharField(
        "رنگ عنوان اصلی", max_length=20, default="#ffffff"
    )
    hero_title_first_word_color = models.CharField(
        "رنگ کلمه اول", max_length=20, default="#c1121f"
    )
    hero_title_second_word_color = models.CharField(
        "رنگ کلمه دوم", max_length=20, default="#ffffff"
    )
    hero_subtitle_color = models.CharField(
        "رنگ زیرنویس", max_length=255, default="rgba(255,255,255,0.7)"
    )

    # FONTS
    hero_title_font_size = models.CharField(
        "اندازه فونت عنوان", max_length=20, default="72px"
    )
    hero_subtitle_font_size = models.CharField(
        "اندازه فونت زیرنویس", max_length=20, default="20px"
    )
    hero_title_font_weight = models.CharField(
        "ضخامت فونت عنوان", max_length=20, default="900"
    )

    # HERO BENNER
    hero_banner_height = models.CharField("ارتفاع بنر", max_length=20, default="100vh")
    hero_banner_overlay_opacity = models.CharField(
        "شفافیت لایه رویی", max_length=20, default="0.6"
    )
    hero_background_image = models.ImageField(
        "تصویر پس‌زمینه هیرو",
        upload_to="hero/",
        blank=True,
        null=True,
        help_text="تصویر بنر اصلی (سایز پیشنهادی: 1920x1080)",
    )

    # CTA SECTION
    cta_title = models.CharField(
        "عنوان CTA", max_length=200, default="کلکسیون خود را کامل کنید"
    )
    cta_subtitle = models.CharField(
        "زیرنویس CTA",
        max_length=300,
        blank=True,
        default="با فیگورهای منحصر‌به‌فرد ما، کلکسیون خود را بی‌نظیر کنید",
    )
    cta_button_text = models.CharField(
        "متن دکمه CTA", max_length=50, default="مشاهده همه محصولات"
    )
    cta_button_link = models.CharField(
        "لینک دکمه CTA", max_length=200, default="/products/", blank=True
    )
    cta_background_image = models.ImageField(
        "تصویر پس‌زمینه CTA",
        upload_to="cta/",
        blank=True,
        null=True,
        help_text="تصویر بنر CTA (سایز پیشنهادی: 1200x600)",
    )

    # CTA COLORS
    cta_title_color = models.CharField(
        "رنگ عنوان CTA", max_length=20, default="#ffffff"
    )
    cta_subtitle_color = models.CharField(
        "رنگ زیرنویس CTA", max_length=20, default="#cccccc"
    )
    cta_button_color = models.CharField(
        "رنگ دکمه CTA", max_length=20, default="#c1121f"
    )
    cta_button_text_color = models.CharField(
        "رنگ متن دکمه CTA", max_length=20, default="#ffffff"
    )
    cta_overlay_opacity = models.CharField(
        "شفافیت لایه رویی CTA", max_length=20, default="0.7"
    )
    cta_height = models.CharField("ارتفاع بنر CTA", max_length=20, default="450px")
    cta_border_radius = models.CharField(
        "گردی گوشه‌های CTA", max_length=20, default="30px"
    )

    # بخش محصولات ویژه
    featured_products_title = models.CharField(
        "عنوان بخش محصولات ویژه", max_length=100, default="محصولات ما"
    )
    featured_products_subtitle = models.CharField(
        "زیرنویس بخش محصولات ویژه",
        max_length=200,
        default="مجموعه‌ای از نفیس‌ترین فیگورهای کلکسیونی",
        blank=True,
    )

    # FEAT SECTION
    show_features_section = models.BooleanField("نمایش بخش ویژگی‌ها", default=True)
    features_title = models.CharField(
        "عنوان بخش ویژگی‌ها", max_length=100, default="چرا فیگمکس؟", blank=True
    )

    # FOOTER
    footer_text = models.CharField(
        "متن فوتر", max_length=200, default="مرجع تخصصی مجسمه‌های کلکسیونی"
    )
    footer_copyright = models.CharField(
        "متن کپی‌رایت", max_length=200, default="© 2026 FIGMAX", blank=True
    )

    # PUBLIC SETTING
    site_name = models.CharField("نام سایت", max_length=100, default="FIGMAX")
    site_description = models.CharField(
        "توضیحات سایت",
        max_length=300,
        default="مرجع تخصصی فیگورهای کلکسیونی",
        blank=True,
    )

    updated_at = models.DateTimeField("آخرین بروزرسانی", auto_now=True)

    class Meta:
        verbose_name = "تنظیمات صفحه اصلی"
        verbose_name_plural = "تنظیمات صفحه اصلی"

    def __str__(self):
        return "تنظیمات صفحه اصلی"

    def save(self, *args, **kwargs):
        if not self.pk and HomeSettings.objects.exists():
            return
        super().save(*args, **kwargs)


class Cart(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="cart", null=True, blank=True
    )
    session_key = models.CharField("کلید نشست", max_length=40, blank=True, null=True)
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین بروزرسانی", auto_now=True)

    class Meta:
        verbose_name = "سبد خرید"
        verbose_name_plural = "سبدهای خرید"

    def __str__(self):
        return f"سبد خرید {self.user or self.session_key}"

    def get_total_price(self):
        return sum(item.get_total_price() for item in self.items.all())

    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart, on_delete=models.CASCADE, related_name="items", verbose_name="سبد خرید"
    )
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="محصول")
    quantity = models.PositiveIntegerField("تعداد", default=1)
    added_at = models.DateTimeField("تاریخ اضافه شدن", auto_now_add=True)

    class Meta:
        verbose_name = "آیتم سبد خرید"
        verbose_name_plural = "آیتم‌های سبد خرید"
        unique_together = [["cart", "product"]]

    def __str__(self):
        return f"{self.product.title} - {self.quantity} عدد"

    def get_total_price(self):
        return self.product.price * self.quantity


class Order(models.Model):
    """مدل سفارش"""

    STATUS_CHOICES = (
        ("pending", "در انتظار پرداخت"),
        ("paid", "پرداخت شده"),
        ("processing", "در حال پردازش"),
        ("shipped", "ارسال شده"),
        ("delivered", "تحویل داده شده"),
        ("cancelled", "لغو شده"),
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="shop_orders", verbose_name="کاربر"
    )
    order_number = models.CharField("شماره سفارش", max_length=50, unique=True)
    status = models.CharField(
        "وضعیت", max_length=20, choices=STATUS_CHOICES, default="pending"
    )
    total_price = models.PositiveIntegerField("قیمت کل", default=0)

    # اطلاعات ارسال
    full_name = models.CharField("نام و نام خانوادگی", max_length=200)
    phone = models.CharField("شماره تلفن", max_length=20)
    address = models.TextField("آدرس")
    postal_code = models.CharField("کد پستی", max_length=20, blank=True)

    # اطلاعات پیگیری
    tracking_code = models.CharField(
        "کد پیگیری",
        max_length=100,
        blank=True,
        null=True,
        help_text="کد پیگیری مرسوله پستی یا کد رهگیری",
    )
    delivered_at = models.DateTimeField(
        "تاریخ تحویل",
        blank=True,
        null=True,
        help_text="تاریخی که سفارش به دست مشتری رسیده است",
    )

    # TIMES
    created_at = models.DateTimeField("تاریخ ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین بروزرسانی", auto_now=True)
    paid_at = models.DateTimeField("تاریخ پرداخت", null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "سفارش"
        verbose_name_plural = "سفارشات"

    def __str__(self):
        return f"سفارش #{self.order_number} - {self.user.username}"

    def get_total_price_display(self):
        return f"{self.total_price:,} تومان"


class OrderItem(models.Model):
    """آیتم‌های هر سفارش"""

    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name="shop_items", verbose_name="سفارش"
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="shop_order_items",
        verbose_name="محصول",
    )
    quantity = models.PositiveIntegerField("تعداد", default=1)
    price = models.PositiveIntegerField("قیمت واحد", default=0)

    class Meta:
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"

    def __str__(self):
        return f"{self.product.title} - {self.quantity} عدد"

    def get_total_price(self):
        return self.price * self.quantity


# ============================================
# Signal برای تولید شماره سفارش
# ============================================
@receiver(pre_save, sender=Order)
def generate_order_number(sender, instance, **kwargs):
    if not instance.order_number:
        letters = string.ascii_uppercase
        digits = string.digits
        order_number = "".join(random.choices(letters, k=3)) + "".join(
            random.choices(digits, k=6)
        )
        instance.order_number = order_number
