from django.conf import settings

def shop_context(request):
    """
    Global context processor for shop application
    Adds common data to all templates
    """
    return {
        'shop_settings': {
            'SITE_NAME': 'Dress Shop Management',
            'VERSION': '2.0',
        },
        'media_url': settings.MEDIA_URL,
        'static_url': settings.STATIC_URL,
    }
