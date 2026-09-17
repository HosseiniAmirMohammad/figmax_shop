from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import user_passes_test
import os
import mimetypes

# ONLY SUPERUSERS
def superuser_required(user):
    return user.is_superuser

# Custom view to serve media files in production
def serve_media(request, file_path):
    """Serve media files in production"""
    file_path = os.path.join(settings.MEDIA_ROOT, file_path)
    if os.path.exists(file_path):
        content_type, _ = mimetypes.guess_type(file_path)
        with open(file_path, 'rb') as f:
            return HttpResponse(f.read(), content_type=content_type or 'application/octet-stream')
    raise Http404("File not found")

# ============================================
# فایل تایید اینماد (e-namad)
# فایل خالی 79221564.txt در ریشه وب‌سایت (settings.BASE_DIR) قرار دارد
# و از طریق آدرس https://figmaxshop.ir/79221564.txt در دسترس می‌باشد
# ============================================
ENAMAD_VERIFICATION_FILE = "79221564.txt"


def enamad_verification(request):
    """سرو کردن فایل خالی تایید اینماد از ریشه پروژه"""
    file_path = os.path.join(settings.BASE_DIR, ENAMAD_VERIFICATION_FILE)
    if os.path.exists(file_path):
        with open(file_path, "rb") as f:
            content = f.read()
        response = HttpResponse(content, content_type="text/plain; charset=utf-8")
        response["Content-Length"] = str(len(content))
        return response
    raise Http404("File not found")


urlpatterns = [
    # فایل تایید اینماد - https://figmaxshop.ir/79221564.txt
    path(ENAMAD_VERIFICATION_FILE, enamad_verification, name='enamad_verification'),
    path('admin/', admin.site.urls),
    path('', include('apps.shop.urls')),
    path('', include('apps.accounts.urls')),
    # ADMIN PANNEL ONLY FOR SUPERS
    path('admin-dashboard/', user_passes_test(superuser_required)(include('apps.shop.urls'))),
    # Serve media files
    path('media/<path:file_path>', serve_media, name='serve_media'),
]