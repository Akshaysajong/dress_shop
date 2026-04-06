"""
Cache test views to demonstrate Django caching functionality.
"""

from django.shortcuts import render
from django.views.decorators.cache import cache_page
from django.http import JsonResponse
from django.core.cache import cache
from django.utils import timezone
import time


@cache_page(60)  # Cache for 1 minute
def cached_page_view(request):
    """
    Simple cached page view.
    """
    current_time = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
    
    context = {
        'title': 'Cached Page Test',
        'current_time': current_time,
        'cache_info': 'This page is cached for 60 seconds',
        'timestamp': time.time(),
    }
    
    return render(request, 'cache_test.html', context)


def cache_api_test(request):
    """
    API endpoint to test cache functionality.
    """
    # Try to get cached data
    cache_key = 'api_test_data'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return JsonResponse({
            'status': 'cached',
            'data': cached_data,
            'message': 'Data retrieved from cache',
            'timestamp': timezone.now().isoformat(),
        })
    
    # Generate new data and cache it
    data = {
        'products_count': 42,
        'users_count': 128,
        'orders_count': 256,
        'generated_at': timezone.now().isoformat(),
    }
    
    cache.set(cache_key, data, timeout=30)  # Cache for 30 seconds
    
    return JsonResponse({
        'status': 'fresh',
        'data': data,
        'message': 'Data generated and cached',
        'timestamp': timezone.now().isoformat(),
    })


def cache_status_view(request):
    """
    View to show cache status and statistics.
    """
    try:
        # Test cache connection
        cache.set('status_test', 'ok', timeout=10)
        test_result = cache.get('status_test')
        
        cache_status = 'working' if test_result == 'ok' else 'failed'
        
        # Get cache info
        cache_info = {
            'backend': 'django_redis.cache.RedisCache',
            'location': 'redis://redis:6379/0',
            'status': cache_status,
            'key_prefix': 'dress_shop',
            'timeout': 300,
        }
        
        return JsonResponse({
            'cache_info': cache_info,
            'timestamp': timezone.now().isoformat(),
        })
        
    except Exception as e:
        return JsonResponse({
            'cache_info': {'status': 'error', 'error': str(e)},
            'timestamp': timezone.now().isoformat(),
        })
