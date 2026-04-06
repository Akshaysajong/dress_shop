"""
Example views with caching implementation for the dress shop.
"""

from django.shortcuts import render, get_object_or_404
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers, vary_on_cookie
from django.core.cache import cache
from django.db import models
from django.http import JsonResponse
from .models import Product, Category
from .cache_utils import cache_product_detail, cache_category_list, cache_search_results


@cache_page(300)  # Cache for 5 minutes
@vary_on_headers('User-Agent')
def product_list_cached(request):
    """
    Product list view with page caching.
    """
    products = Product.objects.select_related('category').prefetch_related('images').all()
    
    context = {
        'products': products,
        'categories': cache_category_list(),
    }
    
    return render(request, 'shop_public/product_list.html', context)


@vary_on_cookie
def product_detail_cached(request, product_id):
    """
    Product detail view with object-level caching.
    """
    product = cache_product_detail(product_id)
    
    if not product:
        return JsonResponse({'error': 'Product not found'}, status=404)
    
    # Get related products (with caching)
    cache_key = f"related_products:{product_id}"
    related_products = cache.get(cache_key)
    
    if related_products is None:
        related_products = Product.objects.filter(
            category=product.category
        ).exclude(id=product_id)[:4]
        cache.set(cache_key, related_products, 600)  # Cache for 10 minutes
    
    context = {
        'product': product,
        'related_products': related_products,
    }
    
    return render(request, 'shop_public/product_detail.html', context)


@cache_page(900)  # Cache for 15 minutes
def category_list_cached(request):
    """
    Category list view with caching.
    """
    categories = cache_category_list()
    
    context = {
        'categories': categories,
    }
    
    return render(request, 'shop_public/category_list.html', context)


def search_cached(request):
    """
    Search functionality with caching.
    """
    query = request.GET.get('q', '').strip()
    
    if not query:
        return JsonResponse({'results': [], 'message': 'Empty search query'})
    
    # Cache search results
    results = cache_search_results(query)
    
    # Format results for JSON response
    products_data = []
    for product in results:
        products_data.append({
            'id': product.id,
            'name': product.name,
            'price': str(product.price),
            'image': product.main_image.url if product.main_image else None,
            'category': product.category.name,
        })
    
    return JsonResponse({
        'results': products_data,
        'query': query,
        'count': len(products_data)
    })


def cache_stats_api(request):
    """
    API endpoint to show cache statistics.
    """
    from .cache_utils import get_cache_stats
    
    stats = get_cache_stats()
    return JsonResponse(stats)


def clear_cache_api(request):
    """
    API endpoint to clear cache (for development/testing).
    """
    if request.method == 'POST':
        cache.clear()
        return JsonResponse({'message': 'Cache cleared successfully'})
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)


# Template Tags Example
class CacheTemplateTags:
    """
    Custom template tags for caching.
    """
    
    @staticmethod
    def cached_product_count(category_id):
        """
        Cache product count for a category.
        """
        cache_key = f"product_count:{category_id}"
        count = cache.get(cache_key)
        
        if count is None:
            from .models import Category
            category = Category.objects.get(id=category_id)
            count = category.products.count()
            cache.set(cache_key, count, 300)  # Cache for 5 minutes
        
        return count
    
    @staticmethod
    def cached_featured_products(limit=8):
        """
        Cache featured products.
        """
        cache_key = f"featured_products:{limit}"
        products = cache.get(cache_key)
        
        if products is None:
            products = Product.objects.filter(
                featured=True
            ).select_related('category')[:limit]
            cache.set(cache_key, products, 600)  # Cache for 10 minutes
        
        return products
