from django.shortcuts import render, get_object_or_404
from shop.models import Product, ProductVariant


def home(request):
    """Home page with featured products"""
    # Get featured products
    featured_products = Product.objects.filter(
        is_featured=True, 
        is_active=True
    ).select_related('brand').prefetch_related('variants')[:8]
    
    # Get latest products
    latest_products = Product.objects.filter(
        is_active=True
    ).select_related('brand').prefetch_related('variants').order_by('-created_at')[:8]
    
    context = {
        'featured_products': featured_products,
        'latest_products': latest_products,
    }
    return render(request, 'shop_public/home.html', context)


def product_detail(request, slug):
    """Product detail page"""
    product = get_object_or_404(Product, slug=slug, is_active=True)
    product_variants = product.variants.select_related('size', 'color').all()
    
    # Get related products
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'product_variants': product_variants,
        'related_products': related_products,
    }
    return render(request, 'shop_public/product_detail.html', context)


def about(request):
    """About page"""
    context = {
        'title': 'About Us',
    }
    return render(request, 'shop_public/about.html', context)


def contact(request):
    """Contact page"""
    context = {
        'title': 'Contact Us',
    }
    return render(request, 'shop_public/contact.html', context)


def products_list(request):
    """Products listing page - all products displayed"""
    products = Product.objects.filter(is_active=True).select_related('brand').prefetch_related('variants')
    
    # Filter by category
    category = request.GET.get('category')
    if category:
        products = products.filter(category=category)
    
    # Search
    search = request.GET.get('search')
    if search:
        products = products.filter(name__icontains=search)
    
    # Debug: Check products
    print(f"DEBUG: Total products found: {products.count()}")
    
    context = {
        'products': products,
        'category': category,
        'search': search,
        'total_products': products.count(),
    }
    
    return render(request, 'shop_public/products_list.html', context)
