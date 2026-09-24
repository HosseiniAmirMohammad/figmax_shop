# apps/shop/admin.py

from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import (
    Product,
    ProductImage,
    ProductSpecification,
    SimilarProduct,
    ProductReview,
    Category,
    BannerSlide,
    HomeSettings,
    Cart,
    CartItem,
    Order,
    OrderItem,
)


# فرم سفارشی برای محصول (قیمت با کاما)
class ProductForm(forms.ModelForm):
    price = forms.CharField(
        label="قیمت (تومان)", help_text="مثلاً: 312,000 یا 312000", required=True
    )

    class Meta:
        model = Product
        fields = "__all__"

    def clean_price(self):
        price = self.cleaned_data["price"]
        price = price.replace(",", "").replace(" ", "")
        try:
            return int(price)
        except ValueError:
            raise forms.ValidationError("لطفاً یک عدد معتبر وارد کنید")


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 3
    fields = ("image_preview", "image", "alt_text", "is_main", "order")
    readonly_fields = ("image_preview",)
    ordering = ["order"]

    def image_preview(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" width="80" height="80" style="object-fit:cover; border-radius:8px;"/>',
                obj.image.url,
            )
        return "-"

    image_preview.short_description = "پیش‌نمایش"


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 3
    fields = ("key", "value", "order")
    ordering = ["order"]
    verbose_name = "مشخصه"
    verbose_name_plural = "مشخصات"


class SimilarProductInline(admin.TabularInline):
    model = SimilarProduct
    extra = 3
    fk_name = "product"
    fields = ("similar", "order")
    ordering = ["order"]
    verbose_name = "محصول مشابه"
    verbose_name_plural = "محصولات مشابه"


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 1
    fields = ("product", "quantity")
    readonly_fields = ("product", "quantity")
    verbose_name = "آیتم"
    verbose_name_plural = "آیتم‌ها"

    def has_add_permission(self, request, obj=None):
        return False


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ("product", "quantity", "price")
    readonly_fields = ("product", "quantity", "price")
    verbose_name = "آیتم سفارش"
    verbose_name_plural = "آیتم‌های سفارش"

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order", "is_active")
    list_editable = ("order", "is_active")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductForm
    list_display = (
        "title",
        "price_display",
        "stock",
        "is_active",
        "is_featured",
        "category",
        "created_at",
    )
    list_editable = ("stock", "is_active", "is_featured")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "about_product", "character_story", "short_description")
    list_filter = ("category", "is_active", "is_featured", "created_at")
    inlines = [ProductImageInline, ProductSpecificationInline, SimilarProductInline]
    fieldsets = (
        (
            "اطلاعات اصلی",
            {"fields": ("title", "slug", "category", "price", "short_description")},
        ),
        (
            "توضیحات محصول",
            {
                "fields": ("about_product", "character_story"),
            },
        ),
        (
            "بنر اختصاصی محصول",
            {
                "fields": ("banner_image", "banner_title", "banner_subtitle"),
                "description": "تصویر بنر بالای صفحه محصول (سایز پیشنهادی: 1200x400 پیکسل)",
            },
        ),
        ("موجودی و وضعیت", {"fields": ("stock", "is_active", "is_featured")}),
    )
    actions = ["make_active", "make_inactive", "make_featured"]

    def price_display(self, obj):
        return f"{obj.price:,} تومان"

    price_display.short_description = "قیمت"

    def make_active(self, request, queryset):
        queryset.update(is_active=True)

    make_active.short_description = "فعال کردن محصولات انتخاب شده"

    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)

    make_inactive.short_description = "غیرفعال کردن محصولات انتخاب شده"

    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)

    make_featured.short_description = "ویژه کردن محصولات انتخاب شده"


@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "rating", "created_at")
    list_filter = ("rating", "created_at")
    search_fields = ("product__title", "user__username", "comment")
    ordering = ("-created_at",)


@admin.register(BannerSlide)
class BannerSlideAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_active", "preview_image", "created_at")
    list_editable = ("order", "is_active")
    search_fields = ("title", "subtitle")
    fields = ("title", "subtitle", "image", "link", "order", "is_active")

    def preview_image(self, obj):
        if obj and obj.image:
            return format_html(
                '<img src="{}" width="120" height="70" style="object-fit:cover; border-radius:4px;"/>',
                obj.image.url,
            )
        return "-"

    preview_image.short_description = "پیش‌نمایش"


@admin.register(HomeSettings)
class HomeSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "اطلاعات عمومی سایت",
            {
                "fields": ("site_name", "site_description"),
                "classes": ("wide",),
            },
        ),
        (
            "بخش هیرو - محتوا",
            {
                "fields": ("hero_title", "hero_subtitle", "hero_background_image"),
                "description": "تنظیمات مربوط به بنر اصلی صفحه",
            },
        ),
        (
            "بخش هیرو - رنگ‌ها",
            {
                "fields": (
                    "hero_title_color",
                    "hero_title_first_word_color",
                    "hero_title_second_word_color",
                    "hero_subtitle_color",
                ),
                "description": "رنگ‌های مورد استفاده در بخش هیرو",
                "classes": ("collapse",),
            },
        ),
        (
            "بخش هیرو - فونت و اندازه",
            {
                "fields": (
                    "hero_title_font_size",
                    "hero_title_font_weight",
                    "hero_subtitle_font_size",
                    "hero_banner_height",
                    "hero_banner_overlay_opacity",
                ),
                "description": "اندازه و ضخامت فونت‌ها و ارتفاع بنر",
                "classes": ("collapse",),
            },
        ),
        (
            "بخش CTA (دعوت به اقدام)",
            {
                "fields": (
                    "cta_title",
                    "cta_subtitle",
                    "cta_button_text",
                    "cta_button_link",
                    "cta_background_image",
                    "cta_height",
                ),
                "description": "تنظیمات بنر CTA",
            },
        ),
        (
            "رنگ‌های بخش CTA",
            {
                "fields": (
                    "cta_title_color",
                    "cta_subtitle_color",
                    "cta_button_color",
                    "cta_button_text_color",
                    "cta_overlay_opacity",
                    "cta_border_radius",
                ),
                "description": "رنگ‌های بنر CTA",
                "classes": ("collapse",),
            },
        ),
        (
            "بخش محصولات ویژه",
            {
                "fields": ("featured_products_title", "featured_products_subtitle"),
                "description": "تنظیمات عنوان و زیرنویس بخش محصولات ویژه",
            },
        ),
        (
            "بخش ویژگی‌ها",
            {
                "fields": ("show_features_section", "features_title"),
                "description": "تنظیمات بخش ویژگی‌ها",
                "classes": ("collapse",),
            },
        ),
        (
            "فوتر",
            {
                "fields": ("footer_text", "footer_copyright"),
                "classes": ("collapse",),
            },
        ),
    )

    def has_add_permission(self, request):
        if HomeSettings.objects.exists():
            return False
        return True


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "session_key",
        "get_total_items",
        "get_total_price",
        "created_at",
    )
    list_filter = ("created_at",)
    search_fields = ("user__username", "session_key")
    inlines = [CartItemInline]

    def get_total_items(self, obj):
        return obj.get_total_items()

    get_total_items.short_description = "تعداد آیتم‌ها"

    def get_total_price(self, obj):
        return f"{obj.get_total_price():,} تومان"

    get_total_price.short_description = "قیمت کل"

    def has_add_permission(self, request):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "order_number",
        "user",
        "status",
        "tracking_code_display",
        "total_price_display",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = (
        "order_number",
        "user__username",
        "full_name",
        "phone",
        "tracking_code",
    )
    readonly_fields = ("order_number", "created_at", "updated_at")
    inlines = [OrderItemInline]

    fieldsets = (
        (
            "اطلاعات اصلی سفارش",
            {"fields": ("order_number", "user", "status", "total_price")},
        ),
        ("اطلاعات ارسال", {"fields": ("full_name", "phone", "address", "postal_code")}),
        (
            "پیگیری و تحویل",
            {
                "fields": ("tracking_code", "delivered_at"),
                "description": "کد پیگیری را می‌توانید پس از ارسال سفارش وارد کنید",
            },
        ),
        (
            "زمان‌ها",
            {
                "fields": ("created_at", "updated_at", "paid_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def total_price_display(self, obj):
        return f"{obj.total_price:,} تومان"

    total_price_display.short_description = "قیمت کل"

    def tracking_code_display(self, obj):
        if obj.tracking_code:
            return format_html(
                '<span style="background: #2ecc71; color: #fff; padding: 4px 12px; border-radius: 12px; font-size: 12px;">✅ {}</span>',
                obj.tracking_code,
            )
        return format_html(
            '<span style="background: #666; color: #aaa; padding: 4px 12px; border-radius: 12px; font-size: 12px;">⚠️ ثبت نشده</span>'
        )

    tracking_code_display.short_description = "کد پیگیری"

    def save_model(self, request, obj, form, change):
        # اگر وضعیت به delivered تغییر کرد، تاریخ تحویل ثبت بشه
        if change and "status" in form.changed_data:
            if obj.status == "delivered" and not obj.delivered_at:
                from django.utils import timezone

                obj.delivered_at = timezone.now()
        super().save_model(request, obj, form, change)

    def has_add_permission(self, request):
        return False  # اجازه ایجاد مستقیم سفارش در ادمین نده
