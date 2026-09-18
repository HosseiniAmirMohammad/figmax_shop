from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.http import HttpResponse, Http404
from django.contrib.auth.decorators import user_passes_test
import os
import mimetypes
from . import views

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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.shop.urls')),
    path('', include('apps.accounts.urls')),
    # ADMIN PANNEL ONLY FOR SUPERS
    path('admin-dashboard/', user_passes_test(superuser_required)(include('apps.shop.urls'))),
    # Serve media files
    path('media/<path:file_path>', serve_media, name='serve_media'),
    path('79221564.txt', views.enamad_verify),
]