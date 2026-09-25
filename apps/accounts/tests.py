from django.contrib.auth import get_user_model
from django.test import RequestFactory, TestCase

from apps.accounts.forms import LoginForm


class LoginFormTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="loginuser", email="login@example.com", password="StrongPass123!"
        )
        self.user.profile.phone = "09123456789"
        self.user.profile.save(update_fields=["phone"])

    def test_login_form_passes_request_to_authenticate(self):
        request = RequestFactory().post(
            "/login/", {"identifier": "loginuser", "password": "StrongPass123!"}
        )

        form = LoginForm(request.POST, request=request)

        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["user"], self.user)
