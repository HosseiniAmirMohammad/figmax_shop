from django import template
from django.template.loader import render_to_string
from ..models import HomeSettings

register = template.Library()

@register.simple_tag
def get_home_settings():
    """دریافت تنظیمات صفحه اصلی"""
    try:
        return HomeSettings.objects.first()
    except:
        return None

@register.inclusion_tag('shop/partials/hero_banner.html')
def hero_banner():
    """رندر بنر هیرو با تنظیمات سفارشی"""
    settings = HomeSettings.objects.first()
    return {'settings': settings}

@register.inclusion_tag('shop/partials/cta_banner.html')
def cta_banner():
    """رندر بنر CTA با تنظیمات سفارشی"""
    settings = HomeSettings.objects.first()
    return {'settings': settings}