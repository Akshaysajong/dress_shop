"""
Cache utilities for the dress shop application.
"""

from django.core.cache import cache
from django.conf import settings
from shop.models import Product, Category
import hashlib


def get_cache_key(prefix, *args, **kwargs):
    """
    Generate a unique cache key based on prefix and arguments.
    """
    key_data = f"{prefix}:{args}:{sorted(kwargs.items())}"
    return hashlib.md5(key_data.encode()).hexdigest()


def cache_product_list(timeout=300):
    """
    Cache decorator for product list queries.
    """
    def decorator(view_func):
        def wrapper(*args, **kwargs):
            cache_key = get_cache_key('product_list', *args, **kwargs)
            cached_data = cache.get(cache_key)
            
            if cached_data is not None:
                return cached_data
            
            result = view_func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result
        return wrapper
    return decorator


def cache_product_detail(product_id, timeout=600):
    """
    Cache individual product details.
    """
    cache_key = f"product_detail:{product_id}"
    cached_product = cache.get(cache_key)
    
    if cached_product is not None:
        return cached_product
    
    try:
        product = Product.objects.select_related('category').prefetch_related('images').get(id=product_id)
        cache.set(cache_key, product, timeout)
        return product
    except Product.DoesNotExist:
        return None


def cache_category_list(timeout=900):
    """
    Cache category list with product counts.
    """
    cache_key = 'category_list_with_counts'
    cached_categories = cache.get(cache_key)
    
    if cached_categories is not None:
        return cached_categories
    
    categories = Category.objects.annotate(product_count=models.Count('products'))
    cache.set(cache_key, categories, timeout)
    return categories


def invalidate_product_cache(product_id=None):
    """
    Invalidate product-related cache entries.
    """
    if product_id:
        # Invalidate specific product cache
        cache.delete(f"product_detail:{product_id}")
    
    # Invalidate product list cache
    cache.delete_pattern('product_list:*')
    
    # Invalidate category cache
    cache.delete('category_list_with_counts')


def cache_search_results(query, timeout=180):
    """
    Cache search results.
    """
    cache_key = f"search:{hashlib.md5(query.encode()).hexdigest()}"
    cached_results = cache.get(cache_key)
    
    if cached_results is not None:
        return cached_results
    
    from shop.models import Product
    results = Product.objects.filter(
        models.Q(name__icontains=query) |
        models.Q(description__icontains=query) |
        models.Q(category__name__icontains=query)
    ).distinct()
    
    cache.set(cache_key, results, timeout)
    return results


def get_cache_stats():
    """
    Get basic cache statistics.
    """
    try:
        info = cache.client_info()
        return {
            'connected_clients': info.get('connected_clients', 0),
            'used_memory': info.get('used_memory_human', 'N/A'),
            'keyspace_hits': info.get('keyspace_hits', 0),
            'keyspace_misses': info.get('keyspace_misses', 0),
        }
    except:
        return {'status': 'Cache stats unavailable'}
