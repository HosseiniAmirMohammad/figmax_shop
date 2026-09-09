from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import user_passes_test

# ONLY SUPERUSERS
def superuser_required(user):
    return user.is_superuser

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.shop.urls')),
    path('', include('apps.accounts.urls')),
    # ADMIN PANNEL ONLY FOR SUPERS
    path('admin-dashboard/', user_passes_test(superuser_required)(include('apps.shop.urls'))),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)