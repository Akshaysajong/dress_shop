"""
Custom middleware for cache management.
"""

from django.core.cache import cache
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse
import time
from django.conf import settings


class CacheControlMiddleware(MiddlewareMixin):
    """
    Add cache control headers to responses.
    """
    
    def process_response(self, request, response):
        try:
            # Add cache control headers for static files
            if request.path.startswith('/static/') or request.path.startswith('/media/'):
                response['Cache-Control'] = 'public, max-age=31536000'  # 1 year
            elif request.path.startswith('/api/'):
                # API responses cache for 5 minutes
                response['Cache-Control'] = 'public, max-age=300'
            else:
                # Dynamic pages cache for 5 minutes in production
                if not getattr(settings, 'DEBUG', False):
                    response['Cache-Control'] = 'public, max-age=300'
        except Exception:
            # If cache fails, continue without caching
            pass
        
        return response


class PerformanceMiddleware(MiddlewareMixin):
    """
    Add performance headers and monitor response times.
    """
    
    def process_request(self, request):
        request._start_time = time.time()
    
    def process_response(self, request, response):
        try:
            if hasattr(request, '_start_time'):
                duration = time.time() - request._start_time
                response['X-Response-Time'] = f"{duration:.3f}s"
                
                # Log slow requests
                if duration > 1.0:
                    cache.set(f"slow_request:{request.path}", {
                        'path': request.path,
                        'method': request.method,
                        'duration': duration,
                        'timestamp': time.time()
                    }, 3600)  # Keep for 1 hour
        except Exception:
            # If cache fails, continue without performance monitoring
            pass
        
        return response


class CacheInvalidationMiddleware(MiddlewareMixin):
    """
    Automatically invalidate cache when data changes.
    """
    
    def process_response(self, request, response):
        try:
            # Invalidate cache on POST/PUT/DELETE requests
            if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
                if request.path.startswith('/admin/') or request.path.startswith('/api/'):
                    # Clear all cache on admin changes
                    cache.clear()
                elif request.path.startswith('/shop/'):
                    # Invalidate specific cache patterns
                    self.invalidate_shop_cache(request)
        except Exception:
            # If cache fails, continue without invalidation
            pass
        
        return response
    
    def invalidate_shop_cache(self, request):
        """
        Invalidate shop-related cache entries.
        """
        try:
            # Product-related cache
            if 'product' in request.path:
                cache.delete_pattern('product_list:*')
                cache.delete_pattern('product_detail:*')
                cache.delete_pattern('related_products:*')
                cache.delete_pattern('featured_products:*')
            
            # Category-related cache
            elif 'category' in request.path:
                cache.delete_pattern('category_list:*')
                cache.delete_pattern('product_count:*')
            
            # Search cache
            cache.delete_pattern('search:*')
        except Exception:
            # If cache operations fail, continue
            pass


class RateLimitMiddleware(MiddlewareMixin):
    """
    Simple rate limiting middleware with caching.
    """
    
    def process_request(self, request):
        try:
            # Only rate limit API endpoints
            if not request.path.startswith('/api/'):
                return None
            
            client_ip = self.get_client_ip(request)
            cache_key = f"rate_limit:{client_ip}"
            
            # Get current request count
            request_count = cache.get(cache_key, 0)
            
            # Limit to 100 requests per minute
            if request_count > 100:
                return HttpResponse(
                    '{"error": "Rate limit exceeded"}',
                    status=429,
                    content_type='application/json'
                )
            
            # Increment counter
            cache.set(cache_key, request_count + 1, 60)  # Reset every minute
        except Exception:
            # If cache fails, continue without rate limiting
            pass
        
        return None
    
    def get_client_ip(self, request):
        try:
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            return ip
        except Exception:
            return 'unknown'
