from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.shop.models import Product, ProductReview, Order, OrderItem

User = get_user_model()


class ProductReviewPermissionTests(TestCase):
    def setUp(self):
        self.product = Product.objects.create(
            title="تست محصول",
            slug="test-product",
            price=120000,
            stock=10,
            short_description="توضیح کوتاه",
            about_product="توضیح کامل",
            is_active=True,
        )
        self.buyer = User.objects.create_user(username="buyer", password="12345678")
        self.non_buyer = User.objects.create_user(username="guest", password="12345678")

        self.order = Order.objects.create(
            user=self.buyer,
            order_number="ABC123456",
            full_name="کاربر خریدار",
            phone="09120000000",
            address="آدرس تست",
            postal_code="12345",
            total_price=self.product.price,
            status="paid",
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=1,
            price=self.product.price,
        )

    def test_buyer_can_submit_review(self):
        self.client.force_login(self.buyer)
        response = self.client.post(
            reverse("shop:product_detail", args=[self.product.slug]),
            {"rating": 5, "comment": "خیلی خوب بود"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            ProductReview.objects.filter(user=self.buyer, product=self.product).exists()
        )

    def test_non_buyer_cannot_submit_review(self):
        self.client.force_login(self.non_buyer)
        response = self.client.post(
            reverse("shop:product_detail", args=[self.product.slug]),
            {"rating": 5, "comment": "من نمی‌توانم نظر بدهم"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            ProductReview.objects.filter(
                user=self.non_buyer, product=self.product
            ).exists()
        )
