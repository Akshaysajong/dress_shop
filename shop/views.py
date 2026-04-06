from django.db import transaction
from django.db.models import Prefetch, Q, Sum, Count, Avg, Min, Value
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from decimal import Decimal, getcontext
from math import isfinite
from .forms import (ProductForm, ProductFilterForm, 
                   QuickStockForm, BulkStockForm, StockAdjustmentForm)
from .models import (Product, ProductVariant, Customer, Bill, BillItem, 
                    Brand, Size, Color, Material, StockAdjustment)

# Set decimal context for financial calculations
getcontext().prec = 10

def dashboard(request):
    # Get statistics
    total_products = Product.objects.count()
    total_variants = ProductVariant.objects.count()
    total_customers = Customer.objects.count()
    total_bills = Bill.objects.count()
    
    # Stock by category
    stock_by_category = Product.objects.values('category').annotate(
        total_quantity=Sum('variants__quantity'),
        total_products=Count('id')
    )
    
    # Low stock variants (less than 5)
    low_stock_variants = ProductVariant.objects.filter(quantity__lt=5).select_related('product', 'size', 'color').order_by('quantity')
    
    # Recent bills
    recent_bills = Bill.objects.select_related('customer').order_by('-created_at')[:5]
    
    # Top selling products (by quantity sold)
    top_products = Product.objects.annotate(
        total_sold=Sum('variants__billitem__quantity')
    ).order_by('-total_sold')[:5]
    
    # Featured products
    featured_products = Product.objects.filter(is_featured=True, is_active=True)[:3]
    
    # Low stock alerts by product
    low_stock_products = Product.objects.annotate(
        stock_total=Sum('variants__quantity')
    ).filter(stock_total__lt=10).order_by('stock_total')[:5]
    
    context = {
        'total_products': total_products,
        'total_variants': total_variants,
        'total_customers': total_customers,
        'total_bills': total_bills,
        'stock_by_category': stock_by_category,
        'low_stock_variants': low_stock_variants,
        'low_stock_products': low_stock_products,
        'recent_bills': recent_bills,
        'top_products': top_products,
        'featured_products': featured_products,
    }
    return render(request, 'shop/dashboard.html', context)

def customer_management(request):
    """Customer management view with HTMX support"""
    search_query = request.GET.get('search', '')
    page_number = request.GET.get('page', 1)
    
    # Base queryset - only customers with bills
    customers = Customer.objects.filter(items__isnull=False).distinct().order_by('name')
    
    # Calculate statistics
    total_customers = customers.count()
    total_orders = Bill.objects.filter(customer__in=customers).count()
    avg_orders = total_orders / total_customers if total_customers > 0 else 0
    
    # Apply search filter
    if search_query:
        customers = customers.filter(
            Q(name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(customers, 10)
    page_obj = paginator.get_page(page_number)
    
    # HTMX request - return partial content
    if request.headers.get('HX-Request'):
        return render(request, 'shop/partials/customer_list.html', {
            'customers': page_obj,
            'page_obj': page_obj,
            'is_paginated': page_obj.has_other_pages(),
            'search_query': search_query,
        })
    
    # Full page request
    context = {
        'customers': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'search_query': search_query,
        'total_orders': total_orders,
        'avg_orders': avg_orders,
    }
    return render(request, 'shop/customer_management.html', context)

def edit_customer(request, customer_id):
    """Edit customer with HTMX"""
    customer = get_object_or_404(Customer, id=customer_id)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email', '')
        address = request.POST.get('address', '')
        
        # Validation
        if not name or not phone:
            messages.error(request, 'Name and phone are required')
            return render(request, 'shop/partials/edit_customer_form.html', {
                'customer': customer,
                'error': 'Name and phone are required'
            })
        
        # Check if another customer with same phone exists
        if Customer.objects.filter(phone=phone).exclude(id=customer_id).exists():
            messages.error(request, 'Another customer with this phone number already exists')
            return render(request, 'shop/partials/edit_customer_form.html', {
                'customer': customer,
                'error': 'Another customer with this phone number already exists'
            })
        
        # Update customer
        customer.name = name
        customer.phone = phone
        customer.email = email
        customer.address = address
        customer.save()
        
        messages.success(request, f'Customer "{name}" updated successfully!')
        
        # Return updated customer list
        customers = Customer.objects.all().order_by('name')
        paginator = Paginator(customers, 20)
        page_obj = paginator.get_page(1)
        
        return render(request, 'shop/partials/customer_list.html', {
            'customers': page_obj,
            'page_obj': page_obj,
            'is_paginated': page_obj.has_other_pages(),
            'search_query': '',
        })
    
    # GET request - return form
    return render(request, 'shop/partials/edit_customer_form.html', {
        'customer': customer
    })

def delete_customer(request, customer_id):
    """Delete customer with HTMX"""
    customer = get_object_or_404(Customer, id=customer_id)
    
    # Check if customer has bills
    if customer.items.exists():
        messages.error(request, 'Cannot delete customer with existing bills')
        return JsonResponse({'success': False, 'message': 'Cannot delete customer with existing bills'})
    
    customer_name = customer.name
    customer.delete()
    
    messages.success(request, f'Customer "{customer_name}" deleted successfully!')
    return JsonResponse({'success': True, 'message': 'Customer deleted successfully'})

def customer_detail(request, customer_id):
    """Customer detail view with bills history"""
    customer = get_object_or_404(Customer, id=customer_id)
    bills = customer.items.all().order_by('-created_at')
    
    # Calculate statistics
    total_bills = bills.count()
    total_amount = bills.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    avg_order_value = total_amount / total_bills if total_bills > 0 else Decimal('0')
    
    context = {
        'customer': customer,
        'bills': bills,
        'total_bills': total_bills,
        'total_amount': total_amount,
        'avg_order_value': avg_order_value,
    }
    return render(request, 'shop/customer_detail.html', context)

def product_stock_management(request):
    print(f"DEBUG: Request method: {request.method}")
    print(f"DEBUG: Request POST keys: {list(request.POST.keys())}")
    print(f"DEBUG: Request GET keys: {list(request.GET.keys())}")
    print(f"DEBUG: 'create_product' in POST: {'create_product' in request.POST}")
    form = ProductForm()
    
    # Handle product creation
    if request.method == 'POST':
        if "create_product" in request.POST:
            print("DEBUG: POST request received")
            if 'create_product' in request.POST:
                print("DEBUG: Product creation POST received")
                print(f"DEBUG: POST data keys: {list(request.POST.keys())}")
                
                # Get and validate product name
                name = request.POST.get('name', '').strip()
                print(f"DEBUG: Product name: '{name}'")
                
                if not name:
                    messages.error(request, 'Product name is required!')
                    return redirect('shop:product_stock_management')
                
                
                # Create product from POST data
                product_data = {
                    'name': name,
                    'description': request.POST.get('description', '').strip(),
                    'brand_id': request.POST.get('brand'),
                    'sku': request.POST.get('sku', '').strip(),
                    'category': request.POST.get('category', 'new'),
                    'gender': request.POST.get('gender', 'unisex'),
                    'season': request.POST.get('season', '') or None,
                    'occasion': request.POST.get('occasion', '') or None,
                    'fabric_type': request.POST.get('fabric_type', None),
                    'weight': request.POST.get('weight', None) or None,
                    'base_price': float(request.POST.get('base_price', 0) or 0),
                    'selling_price': float(request.POST.get('selling_price', 0) or 0),
                    'discount_percentage': float(request.POST.get('discount_percentage', 0) or 0),
                    'reorder_level': int(request.POST.get('reorder_level', 5) or 5),
                    'is_featured': request.POST.get('is_featured') == 'on',
                    'is_active': request.POST.get('is_active') == 'on',
                }
                
                # Store materials separately for later assignment
                materials_ids = request.POST.getlist('materials', [])
                
                print(f"DEBUG: Product data: {product_data}")
                
                # Validate required fields
                if not product_data['brand_id']:
                    messages.error(request, 'Brand is required!')
                    return redirect('shop:product_stock_management')
                
                # Validate decimal fields
                if product_data['base_price'] <= 0:
                    messages.error(request, 'Base price must be greater than 0!')
                    return redirect('shop:product_stock_management')
                
                if product_data['selling_price'] <= 0:
                    messages.error(request, 'Selling price must be greater than 0!')
                    return redirect('shop:product_stock_management')
                
                # Handle main image upload
                if 'main_image' in request.FILES:
                    product_data['main_image'] = request.FILES['main_image']
                    print("DEBUG: Main image found in FILES")
                else:
                    messages.error(request, 'Product image is required!')
                    return redirect('shop:product_stock_management')
                print("varient savig..........")
                
                try:
                    print("DEBUG: Attempting to create product...")
                    # Create product
                    product = Product.objects.create(**product_data)
                    print(f"DEBUG: Product created with ID: {product.id}")
                    
                    # Handle materials assignment
                    if materials_ids:
                        product.materials.set(materials_ids)
                        print(f"DEBUG: Materials assigned: {materials_ids}")
                    
                    # Handle variants
                    variant_data = request.POST
                    print(f"DEBUG: Variant data: {variant_data}")
                    variant_count = int(request.POST.get('variants-TOTAL_FORMS', 1))  # Default to 1
                    print(f"DEBUG: Variant count from form: {variant_count}")
                    print(f"DEBUG: All POST data keys: {list(request.POST.keys())}")
                    
                    variants_created = 0
                    for i in range(variant_count):
                        size_id = variant_data.get(f'variants-{i}-size')
                        color_id = variant_data.get(f'variants-{i}-color')
                        quantity = variant_data.get(f'variants-{i}-quantity', 0)
                        price = variant_data.get(f'variants-{i}-price', 0)
                        
                        print(f"DEBUG: Variant {i}: size={size_id}, color={color_id}, quantity={quantity}, price={price}")
                        
                        # Skip if any required field is missing
                        if not all([size_id, color_id, quantity, price]):
                            print(f"DEBUG: Skipping variant {i} - missing required data")
                            continue
                        
                        # Skip if quantity is 0 or negative
                        try:
                            quantity_int = int(quantity)
                            if quantity_int <= 0:
                                print(f"DEBUG: Skipping variant {i} - invalid quantity: {quantity_int}")
                                continue
                        except ValueError:
                            print(f"DEBUG: Skipping variant {i} - invalid quantity format: {quantity}")
                            continue
                            
                        try:
                            # Check if variant already exists
                            existing_variant = ProductVariant.objects.filter(
                                product=product,
                                size_id=size_id,
                                color_id=color_id
                            ).first()
                            
                            if existing_variant:
                                print(f"DEBUG: Variant {i} already exists, updating...")
                                existing_variant.quantity = quantity_int
                                existing_variant.price_override = float(price)
                                existing_variant.save()
                                print(f"DEBUG: Variant {i} updated successfully")
                                variants_created += 1
                            else:
                                variant_data_dict = {
                                    'product': product,
                                    'size_id': size_id,
                                    'color_id': color_id,
                                    'quantity': quantity_int,
                                    'price_override': float(price)
                                }
                                
                                # Handle variant image upload
                                variant_image_key = f'variants-{i}-image'
                                if variant_image_key in request.FILES:
                                    variant_data_dict['image'] = request.FILES[variant_image_key]
                                
                                ProductVariant.objects.create(**variant_data_dict)
                                print(f"DEBUG: Variant {i} created successfully")
                                variants_created += 1
                                
                        except Exception as e:
                            print(f"DEBUG: Error creating variant {i}: {str(e)}")
                            continue
                    
                    print(f"DEBUG: Total variants processed: {variants_created}")
                    
                    messages.success(request, f'Product "{product.name}" has been created successfully!')
                    
                    # Clear cache to refresh statistics
                    cache.delete('stock_management_stats')
                    
                    return redirect('shop:product_stock_management')
                    
                except Exception as e:
                    print(f"DEBUG: Error creating product: {str(e)}")
                    messages.error(request, f'Error creating product: {str(e)}')
                    return redirect('shop:product_stock_management')
            
            elif 'save_as_draft' in request.POST:
                print("DEBUG: Draft saving POST received")
                
                # Get and validate product name
                name = request.POST.get('name', '').strip()
                print(f"DEBUG: Draft product name: '{name}'")
                
                if not name:
                    messages.error(request, 'Product name is required!')
                    return redirect('shop:product_stock_management')
                
                # Create product from POST data
                product_data = {
                    'name': name,
                    'description': request.POST.get('description', '').strip(),
                    'brand_id': request.POST.get('brand'),
                    'sku': request.POST.get('sku', '').strip(),
                    'category': request.POST.get('category', 'new'),
                    'gender': request.POST.get('gender', 'unisex'),
                    'season': request.POST.get('season', '') or None,
                    'occasion': request.POST.get('occasion', '') or None,
                    'fabric_type': request.POST.get('fabric_type', '') or None,
                    'weight': request.POST.get('weight', None) or None,
                    'base_price': float(request.POST.get('base_price', 0) or 0),
                    'selling_price': float(request.POST.get('selling_price', 0) or 0),
                    'discount_percentage': float(request.POST.get('discount_percentage', 0) or 0),
                    'reorder_level': int(request.POST.get('reorder_level', 5) or 5),
                    'is_featured': request.POST.get('is_featured') == 'on',
                    'is_active': request.POST.get('is_active') == 'on',
                }
                
                # Store materials separately for later assignment
                materials_ids = request.POST.getlist('materials', [])
                
                # Validate required fields
                if not product_data['brand_id']:
                    messages.error(request, 'Brand is required!')
                    return redirect('shop:product_stock_management')
                
                # Handle main image upload
                if 'main_image' in request.FILES:
                    product_data['main_image'] = request.FILES['main_image']
                
                try:
                    print("DEBUG: Attempting to create draft product...")
                    # Create product
                    product = Product.objects.create(**product_data)
                    print(f"DEBUG: Draft product created with ID: {product.id}")
                    
                    # Handle materials assignment
                    if materials_ids:
                        product.materials.set(materials_ids)
                        print(f"DEBUG: Materials assigned to draft: {materials_ids}")
                    
                    # Handle variants
                    variant_data = request.POST
                    variant_count = int(request.POST.get('variants-TOTAL_FORMS', 0))
                    
                    for i in range(variant_count):
                        size_id = variant_data.get(f'variants-{i}-size')
                        color_id = variant_data.get(f'variants-{i}-color')
                        quantity = variant_data.get(f'variants-{i}-quantity', 0)
                        price = variant_data.get(f'variants-{i}-price', 0)
                        
                        if size_id and color_id and quantity and price:
                            variant_data = {
                                'product': product,
                                'size_id': size_id,
                                'color_id': color_id,
                                'quantity': int(quantity),
                                'price_override': float(price)
                            }
                            
                            # Handle variant image upload
                            variant_image_key = f'variants-{i}-image'
                            if variant_image_key in request.FILES:
                                variant_data['image'] = request.FILES[variant_image_key]
                            
                            ProductVariant.objects.create(**variant_data)
                    
                    messages.info(request, f'Product "{product.name}" has been saved as draft!')
                    
                    # Clear cache to refresh statistics
                    cache.delete('stock_management_stats')
                    
                    return redirect('shop:product_stock_management')
                
                except Exception as e:
                    print(f"DEBUG: Error saving draft: {str(e)}")
                    messages.error(request, f'Error saving draft: {str(e)}')
                    return redirect('shop:product_stock_management')

        elif "create_brand" in request.POST:
            name = request.POST.get('name', '').strip()
            description = request.POST.get('description', '').strip()
            if not name:
                messages.error(request, 'Brand name is required!')
                return redirect('shop:product_stock_management')

            try:
                # Create new brand
                brand_data = {
                    'name': name,
                    'description': description
                }
                
                # Handle logo upload
                if 'logo' in request.FILES:
                    brand_data['logo'] = request.FILES['logo']
                
                brand = Brand.objects.create(**brand_data)
                messages.success(request, f'Brand "{brand.name}" has been created successfully!')
                
                # Clear form data cache
                cache.delete('form_data_choices')
                
                return redirect('shop:product_stock_management')
                
            except Exception as e:
                print(f"DEBUG: Error creating brand: {str(e)}")
                messages.error(request, f'Error creating brand: {str(e)}')
                return redirect('shop:product_stock_management')

    print("DEBUG: Rendering GET request")
    
    # Apply filters first to limit the dataset
    base_queryset = Product.objects.all()
    has_filters = False
    
    category_filter = request.GET.get('category')
    gender_filter = request.GET.get('gender')
    brand_filter = request.GET.get('brand')
    size_filter = request.GET.get('size')
    color_filter = request.GET.get('color')
    search_query = request.GET.get('search')
    stock_status_filter = request.GET.get('stock_status')
    
    # Apply filters to base queryset
    if category_filter:
        base_queryset = base_queryset.filter(category=category_filter)
        has_filters = True
    if gender_filter:
        base_queryset = base_queryset.filter(gender=gender_filter)
        has_filters = True
    if brand_filter:
        base_queryset = base_queryset.filter(brand__id=brand_filter)
        has_filters = True
    if size_filter:
        base_queryset = base_queryset.filter(variants__size__id=size_filter).distinct()
        has_filters = True
    if color_filter:
        base_queryset = base_queryset.filter(variants__color__id=color_filter).distinct()
        has_filters = True
    if search_query:
        base_queryset = base_queryset.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(brand__name__icontains=search_query)
        )
        has_filters = True
    if stock_status_filter:
        # Annotate with total stock for filtering
        base_queryset = base_queryset.annotate(
            stock_total=Sum('variants__quantity')
        )
        if stock_status_filter == 'out':
            base_queryset = base_queryset.filter(stock_total=0)
        elif stock_status_filter == 'low':
            base_queryset = base_queryset.filter(stock_total__lt=5)
        elif stock_status_filter == 'limited':
            base_queryset = base_queryset.filter(stock_total__lt=20)
        elif stock_status_filter == 'good':
            base_queryset = base_queryset.filter(stock_total__gte=20)
        has_filters = True
    
    # Get filtered products with optimized query
    products = base_queryset.prefetch_related(
        Prefetch('variants', queryset=ProductVariant.objects.select_related('size', 'color'))
    ).select_related('brand').order_by('name')
    
    # Show only 10 products on main page
    products = products[:10]
    
    # Calculate statistics using database queries instead of Python loops
    stats_cache_key = 'stock_management_stats'
    cached_stats = cache.get(stats_cache_key)
    
    if cached_stats is None:
        # Use aggregated queries for better performance
        all_products_stats = Product.objects.annotate(
            stock_total=Sum('variants__quantity')
        ).aggregate(
            total_products=Count('id'),
            good_stock_count=Count('id', filter=Q(stock_total__gte=10)),
            low_stock_count=Count('id', filter=Q(stock_total__lt=10, stock_total__gt=0)),
            out_stock_count=Count('id', filter=Q(stock_total=0)),
            total_stock_value=Sum('variants__quantity'),
            total_variants=Count('variants')
        )
        
        # Stock by category using aggregation
        stock_by_category_data = Product.objects.values('category').annotate(
            total_stock=Sum('variants__quantity')
        ).order_by('category')
        
        stock_by_category = {
            item['category']: item['total_stock'] or 0 
            for item in stock_by_category_data
        }
        
        cached_stats = {
            'good_stock_count': all_products_stats['good_stock_count'] or 0,
            'low_stock_count': all_products_stats['low_stock_count'] or 0,
            'out_stock_count': all_products_stats['out_stock_count'] or 0,
            'total_stock_value': all_products_stats['total_stock_value'] or 0,
            'stock_by_category': stock_by_category,
            'total_variants': all_products_stats['total_variants'] or 0,
            'total_products_count': all_products_stats['total_products'] or 0
        }
        
        # Cache for 5 minutes
        cache.set(stats_cache_key, cached_stats, 300)
    
    # Get form data with single query using values_list
    form_data_cache_key = 'form_data_choices'
    cached_form_data = cache.get(form_data_cache_key)
    
    if cached_form_data is None:
        brands = list(Brand.objects.values('id', 'name'))
        sizes = list(Size.objects.values('id', 'name'))
        colors = list(Color.objects.values('id', 'name', 'hex_code'))
        materials = list(Material.objects.values('id', 'name'))
        
        cached_form_data = {
            'brands': brands,
            'sizes': sizes,
            'colors': colors,
            'materials': materials
        }
        
        # Cache for 10 minutes
        cache.set(form_data_cache_key, cached_form_data, 600)
    
    categories = Product.CATEGORY_CHOICES
    genders = Product.GENDER_CHOICES
    seasons = Product.SEASON_CHOICES
    occasions = Product.OCCASION_CHOICES
    
    context = {
        'form' : form,
        'products': products,
        'total_products': cached_stats['total_products_count'],
        'good_stock_count': cached_stats['good_stock_count'],
        'low_stock_count': cached_stats['low_stock_count'],
        'out_stock_count': cached_stats['out_stock_count'],
        'total_stock_value': cached_stats['total_stock_value'],
        'stock_by_category': cached_stats['stock_by_category'],
        'total_variants': cached_stats['total_variants'],
        'has_filters': has_filters,
        'brands': cached_form_data['brands'],
        'sizes': cached_form_data['sizes'],
        'colors': cached_form_data['colors'],
        'materials': cached_form_data['materials'],
        'categories': categories,
        'genders': genders,
        'seasons': seasons,
        'occasions': occasions,
        'current_category': category_filter,
        'current_gender': gender_filter,
        'current_brand': brand_filter,
        'current_size': size_filter,
        'current_color': color_filter,
        'search_query': search_query,
        'stock_status_filter': stock_status_filter,
    }
    
    return render(request, 'shop/product_stock_management.html', context)

def add_brand(request):
    """Handle brand creation via AJAX or form submission"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if not name:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': 'Brand name is required'})
            else:
                messages.error(request, 'Brand name is required!')
                return redirect('shop:add_brand')
        
        try:
            # Create new brand
            brand_data = {
                'name': name,
                'description': description
            }
            
            # Handle logo upload
            if 'logo' in request.FILES:
                brand_data['logo'] = request.FILES['logo']
            
            brand = Brand.objects.create(**brand_data)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True, 
                    'brand': {
                        'id': brand.id,
                        'name': brand.name,
                        'description': brand.description
                    }
                })
            else:
                messages.success(request, f'Brand "{brand.name}" has been created successfully!')
                return redirect('shop:add_brand')
                
        except Exception as e:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'error': str(e)})
            else:
                messages.error(request, f'Error creating brand: {str(e)}')
                return redirect('shop:add_brand')
    
    # For GET requests, return existing brands (for AJAX calls)
    return JsonResponse({'success': True, 'brands': list(Brand.objects.values('id', 'name', 'description'))})


def product_list(request):
    products = Product.objects.prefetch_related(
        Prefetch('variants', queryset=ProductVariant.objects.select_related('size', 'color'))
    ).select_related('brand').order_by('name')
    
    # Filtering
    category_filter = request.GET.get('category')
    gender_filter = request.GET.get('gender')
    brand_filter = request.GET.get('brand')
    size_filter = request.GET.get('size')
    color_filter = request.GET.get('color')
    search_query = request.GET.get('search')
    
    if category_filter:
        products = products.filter(category=category_filter)
    if gender_filter:
        products = products.filter(gender=gender_filter)
    if brand_filter:
        products = products.filter(brand__id=brand_filter)
    if size_filter:
        products = products.filter(variants__size__id=size_filter).distinct()
    if color_filter:
        products = products.filter(variants__color__id=color_filter).distinct()
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(brand__name__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(products, 10)  # Show 20 products per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number or 1)
    
    context = {
        'products': page_obj,
        'page_obj': page_obj,
        'categories': Product.CATEGORY_CHOICES,
        'genders': Product.GENDER_CHOICES,
        'brands': Brand.objects.all(),
        'sizes': Size.objects.all(),
        'colors': Color.objects.all(),
        'current_category': category_filter,
        'current_gender': gender_filter,
        'current_brand': brand_filter,
        'current_size': size_filter,
        'current_color': color_filter,
        'search_query': search_query,
    }
    return render(request, 'shop/product_list.html', context)

def product_detail(request, product_slug):
    product = get_object_or_404(Product.objects.prefetch_related(
        'variants__size',
        'variants__color',
        'variants',
        'materials'
    ).select_related('brand'), slug=product_slug)

    print("product:", product)
    
    # Get available sizes and colors
    available_sizes = set()
    available_colors = set()
    for variant in product.variants.all():
        if variant.quantity > 0:
            available_sizes.add(variant.size)
            available_colors.add(variant.color)
    
    context = {
        'product': product,
        'available_sizes': sorted(available_sizes, key=lambda x: x.order),
        'available_colors': available_colors,
    }
    return render(request, 'shop/product_detail.html', context)

def product_edit(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        
        if form.is_valid():
            form.save()
            messages.success(request, f'Product "{product.name}" has been updated successfully!')
            return redirect('shop:product_detail', product_slug=product.slug)
    else:
        form = ProductForm(instance=product)
    
    # Get data for form choices
    brands = Brand.objects.all().order_by('name')
    colors = Color.objects.all().order_by('name')
    sizes = Size.objects.all().order_by('order')
    materials = Material.objects.all().order_by('name')
    
    context = {
        'form': form,
        'product': product,
        'brands': brands,
        'colors': colors,
        'sizes': sizes,
        'materials': materials,
        'title': f'Edit Product: {product.name}',
        'button_text': 'Update Product',
        'is_edit': True,
    }
    return render(request, 'shop/product_form.html', context)

def add_stock(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 0))
        reason = request.POST.get('reason', 'Manual stock addition')
        
        if quantity > 0:
            # Create stock adjustment record
            StockAdjustment.objects.create(
                product_variant=variant,
                adjustment_type='purchase',
                quantity_before=variant.quantity,
                quantity_after=variant.quantity + quantity,
                quantity_changed=quantity,
                reason=reason,
                created_by='Shop User'  # In real app, use request.user
            )
            
            variant.quantity += quantity
            variant.save()
            messages.success(request, f'Added {quantity} items to {variant.product.name} - {variant.size.name} - {variant.color.name}')
        else:
            messages.error(request, 'Invalid quantity')
    return redirect('product_list')

def reduce_stock(request, variant_id):
    variant = get_object_or_404(ProductVariant, id=variant_id)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 0))
        reason = request.POST.get('reason', 'Manual stock reduction')
        
        if quantity > 0 and variant.quantity >= quantity:
            # Create stock adjustment record
            StockAdjustment.objects.create(
                product_variant=variant,
                adjustment_type='adjustment',
                quantity_before=variant.quantity,
                quantity_after=variant.quantity - quantity,
                quantity_changed=-quantity,
                reason=reason,
                created_by='Shop User'  # In real app, use request.user
            )
            
            variant.quantity -= quantity
            variant.save()
            messages.success(request, f'Reduced {quantity} items from {variant.product.name} - {variant.size.name} - {variant.color.name}')
        else:
            messages.error(request, 'Invalid quantity or insufficient stock')
    return redirect('product_list')

def quick_add_stock(request):
    if request.method == 'POST':
        variant_id = request.POST.get('variant_id')
        quantity = int(request.POST.get('quantity', 0))
        reason = request.POST.get('reason', 'Quick stock addition')
        
        if variant_id and quantity > 0:
            variant = get_object_or_404(ProductVariant, id=variant_id)
            
            # Create stock adjustment record
            StockAdjustment.objects.create(
                product_variant=variant,
                adjustment_type='purchase',
                quantity_before=variant.quantity,
                quantity_after=variant.quantity + quantity,
                quantity_changed=quantity,
                reason=reason,
                created_by=request.user.username if request.user.is_authenticated else 'Shop User'
            )
            
            variant.quantity += quantity
            variant.save()
            
            messages.success(request, f'Added {quantity} items to {variant.product.name} - {variant.size.name} - {variant.color.name}')
        else:
            messages.error(request, 'Invalid data provided')
    
    return redirect('shop:stock_management')

def bulk_stock_operation(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        quantity = int(request.POST.get('quantity', 0))
        apply_to = request.POST.get('apply_to')
        reason = request.POST.get('reason', 'Bulk stock operation')
        
        if action and quantity >= 0:
            products = Product.objects.all()
            
            # Apply filtering based on apply_to
            if apply_to == 'category':
                category = request.POST.get('category')
                if category:
                    products = products.filter(category=category)
            elif apply_to == 'individual':
                product_ids = request.POST.getlist('product_ids')
                if product_ids:
                    products = products.filter(id__in=product_ids)
            
            adjustments_made = 0
            for product in products:
                for variant in product.variants.all():
                    quantity_before = variant.quantity
                    quantity_after = quantity_before
                    
                    if action == 'add':
                        quantity_after = quantity_before + quantity
                    elif action == 'reduce':
                        quantity_after = max(0, quantity_before - quantity)
                    elif action == 'set':
                        quantity_after = quantity
                    
                    if quantity_after != quantity_before:
                        StockAdjustment.objects.create(
                            product_variant=variant,
                            adjustment_type='bulk_operation',
                            quantity_before=quantity_before,
                            quantity_after=quantity_after,
                            quantity_changed=quantity_after - quantity_before,
                            reason=f"{reason} - {action}",
                            created_by=request.user.username if request.user.is_authenticated else 'Shop User'
                        )
                        
                        variant.quantity = quantity_after
                        variant.save()
                        adjustments_made += 1
            
            messages.success(request, f'Bulk operation completed. {adjustments_made} variants updated.')
        else:
            messages.error(request, 'Invalid operation parameters')
    
    return redirect('shop:stock_management')

def stock_history(request):
    # Get all adjustments with related data
    adjustments = StockAdjustment.objects.select_related(
        'product_variant__product', 'product_variant__size', 'product_variant__color'
    ).order_by('-created_at')
    
    # Get products for filter dropdown
    products = Product.objects.filter(
        id__in=StockAdjustment.objects.values_list('product_variant__product_id', flat=True).distinct()
    ).order_by('name')
    
    # Apply filters
    adjustment_type = request.GET.get('adjustment_type')
    product_id = request.GET.get('product_id')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    if adjustment_type:
        adjustments = adjustments.filter(adjustment_type=adjustment_type)
    if product_id:
        adjustments = adjustments.filter(product_variant__product_id=product_id)
    if start_date:
        adjustments = adjustments.filter(created_at__date__gte=start_date)
    if end_date:
        adjustments = adjustments.filter(created_at__date__lte=end_date)
    
    # Calculate statistics
    stats = {
        'total_adjustments': adjustments.count(),
        'stock_added': adjustments.filter(quantity_changed__gt=0).count(),
        'stock_reduced': adjustments.filter(quantity_changed__lt=0).count(),
        'today_activity': adjustments.filter(created_at__date=timezone.now().date()).count(),
    }
    
    # Pagination
    paginator = Paginator(adjustments, 50)  # 50 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'adjustments': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'adjustment_types': StockAdjustment.ADJUSTMENT_TYPES,
        'products': products,
        'stats': stats,
        'current_filters': {
            'adjustment_type': adjustment_type,
            'product_id': product_id,
            'start_date': start_date,
            'end_date': end_date,
        }
    }
    return render(request, 'shop/stock_history.html', context)

def bill_list(request):
    bills = Bill.objects.select_related('customer').order_by('-created_at')
    
    # Filtering
    status_filter = request.GET.get('status')
    payment_filter = request.GET.get('payment_method')
    search_query = request.GET.get('search')
    
    if status_filter:
        bills = bills.filter(status=status_filter)
    if payment_filter:
        bills = bills.filter(payment_method=payment_filter)
    if search_query:
        bills = bills.filter(
            Q(bill_number__icontains=search_query) |
            Q(customer__name__icontains=search_query) |
            Q(customer__phone__icontains=search_query)
        )
    
    # Calculate statistics
    total_revenue = bills.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
    total_bills = bills.count()
    avg_bill_amount = total_revenue / total_bills if total_bills > 0 else Decimal('0')
    
    # Pagination
    paginator = Paginator(bills, 10)  # Show 10 bills per page
    page_number = request.GET.get('page', '1')
    try:
        page_number = int(page_number)
    except (ValueError, TypeError):
        page_number = 1
    page_obj = paginator.get_page(page_number)
    
    # Create page range for template
    total_pages = paginator.num_pages
    current_page = page_obj.number
    start_page = max(1, current_page - 3)
    end_page = min(total_pages, current_page + 3)
    page_range = range(start_page, end_page + 1)
    
    context = {
        'bills': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'page_range': page_range,
        'total_pages': total_pages,
        'status_choices': Bill.STATUS_CHOICES,
        'payment_methods': Bill.PAYMENT_METHODS,
        'current_status': status_filter,
        'current_payment': payment_filter,
        'search_query': search_query,
        'total_revenue': total_revenue,
        'total_bills': total_bills,
        'avg_bill_amount': avg_bill_amount,
    }
    
    # Check if this is an HTMX request
    if request.headers.get('HX-Request'):
        return render(request, 'shop/bill_list_partial.html', context)
    
    return render(request, 'shop/bill_list.html', context)

def create_bill(request):
    if request.method == 'POST':
        try:
            customer_name = request.POST.get('customer_name')
            customer_phone = request.POST.get('customer_phone')
            customer_email = request.POST.get('customer_email', '')
            payment_method = request.POST.get('payment_method', 'cash')
            
            # Validate required fields
            if not customer_name or not customer_phone:
                messages.error(request, 'Customer name and phone are required')
                return render(request, 'shop/create_bill.html', {
                    'variants': ProductVariant.objects.filter(quantity__gt=0).select_related(
                        'product', 'size', 'color'
                    ).order_by('product__name', 'size__order', 'color__name'),
                    'payment_methods': Bill.PAYMENT_METHODS,
                })
            
            # Create or get customer
            customer, created = Customer.objects.get_or_create(
                phone=customer_phone,
                defaults={
                    'name': customer_name,
                    'email': customer_email
                }
            )
            
            # Create bill with temporary bill number
            bill = Bill.objects.create(
                customer=customer,
                bill_number=f"TEMP-{timezone.now().strftime('%Y%m%d%H%M%S')}",  # Unique temporary number
                subtotal=0,
                discount_amount=0,
                tax_amount=0,
                total_amount=0,
                payment_method=payment_method,
                status='paid'
            )
            
            # Process bill items efficiently
            variant_ids = request.POST.getlist('variant_id')
            quantities = request.POST.getlist('quantity')
            
            subtotal = Decimal('0')
            items_to_create = []
            stock_updates = []
            
            for i, variant_id in enumerate(variant_ids):
                if variant_id and i < len(quantities):
                    variant = get_object_or_404(ProductVariant, id=variant_id)
                    quantity = int(quantities[i])
                    
                    if quantity > 0 and variant.quantity >= quantity:
                        # Calculate price
                        if variant.price_override:
                            if variant.product.discount_percentage > 0:
                                discount_factor = Decimal('1') - (Decimal(str(variant.product.discount_percentage)) / Decimal('100'))
                                unit_price = Decimal(str(variant.price_override)) * discount_factor
                            else:
                                unit_price = Decimal(str(variant.price_override))
                        else:
                            if variant.product.discount_percentage > 0:
                                discount_factor = Decimal('1') - (Decimal(str(variant.product.discount_percentage)) / Decimal('100'))
                                unit_price = Decimal(str(variant.product.selling_price)) * discount_factor
                            else:
                                unit_price = Decimal(str(variant.product.selling_price))
                        
                        quantity_decimal = Decimal(quantity)
                        total_price = unit_price * quantity_decimal
                        
                        # Prepare data for bulk operations
                        items_to_create.append(BillItem(
                            bill=bill,
                            product_variant=variant,
                            product=variant.product,
                            quantity=quantity,
                            unit_price=unit_price,
                            total=total_price
                        ))
                        
                        stock_updates.append({
                            'variant': variant,
                            'quantity_change': -quantity,
                            'reason': f'sale - Bill #{bill.bill_number}'
                        })
                        
                        subtotal += total_price
            
            # Bulk create bill items
            if items_to_create:
                BillItem.objects.bulk_create(items_to_create)
                items_created = True
            
            # Bulk update stock
            for update in stock_updates:
                variant = update['variant']
                quantity_change = update['quantity_change']
                StockAdjustment.objects.create(
                    product_variant=variant,
                    adjustment_type='return',
                    quantity_before=variant.quantity,
                    quantity_after=variant.quantity + quantity_change,
                    quantity_changed=quantity_change,
                    reason=update['reason'],
                    created_by='Shop User'
                )
                variant.quantity += quantity_change
                variant.save()
            
            if not items_created:
                messages.error(request, 'Please add at least one valid item to the bill')
                bill.delete()
                return render(request, 'shop/create_bill.html', {
                    'variants': ProductVariant.objects.filter(quantity__gt=0).select_related(
                        'product', 'size', 'color'
                    ).order_by('product__name', 'size__order', 'color__name'),
                    'payment_methods': Bill.PAYMENT_METHODS,
                })
            
            # Update bill totals with Decimal values
            bill.subtotal = subtotal  # subtotal is already Decimal
            bill.total_amount = subtotal  # subtotal is already Decimal
            bill.save()
            
            # Generate proper bill number after saving
            # Get the highest bill number for today to ensure uniqueness
            today_prefix = f"BILL-{timezone.now().strftime('%Y%m%d')}"
            latest_bill = Bill.objects.filter(bill_number__startswith=today_prefix).order_by('-bill_number').first()
            
            if latest_bill:
                # Extract the sequence number and increment
                try:
                    last_sequence = int(latest_bill.bill_number.split('-')[-1])
                    new_sequence = last_sequence + 1
                except (ValueError, IndexError):
                    new_sequence = 1
            else:
                new_sequence = 1
            
            bill.bill_number = f"{today_prefix}-{new_sequence:04d}"
            bill.save()
            
            messages.success(request, f'Bill #{bill.bill_number} created successfully!')
            
            # Send bill email using Celery
            try:
                from .tasks import send_bill_email_task
                if customer_email:
                    send_bill_email_task.delay(bill.id, customer_email)
                else:
                    send_bill_email_task.delay(bill.id)
                messages.info(request, 'Bill is being sent to customer email...')
            except Exception as email_error:
                messages.warning(request, f'Bill created but email sending failed: {str(email_error)}')
            
            return redirect('shop:bill_detail', bill_number=bill.bill_number)
            
        except Exception as e:
            messages.error(request, f'Error creating bill: {str(e)}')
            return render(request, 'shop/create_bill.html', {
                'variants': ProductVariant.objects.filter(quantity__gt=0).select_related(
                    'product', 'size', 'color'
                ).order_by('product__name', 'size__order', 'color__name'),
                'payment_methods': Bill.PAYMENT_METHODS,
            })
    
    # Get available variants with stock - optimized query
    variants = ProductVariant.objects.filter(
        quantity__gt=0
    ).select_related(
        'product', 'size', 'color'
    ).order_by('product__name', 'size__order', 'color__name')
    
    context = {
        'variants': variants,
        'payment_methods': Bill.PAYMENT_METHODS,
    }
    return render(request, 'shop/create_bill.html', context) 

def bill_detail(request, bill_number):
    bill = get_object_or_404(Bill.objects.prefetch_related(
        'items__product_variant__product',
        'items__product_variant__size',
        'items__product_variant__color'
    ).select_related('customer'), bill_number=bill_number)
    return render(request, 'shop/bill_detail.html', {'bill': bill})

def search_customer_by_phone(request):
    """Search for existing customer by phone number"""
    phone = request.GET.get('phone', '').strip()
    if not phone:
        return JsonResponse({'error': 'Phone number is required'}, status=400)
    
    try:
        customers = Customer.objects.filter(phone__icontains=phone)
        
        if customers.count() == 1:
            # Single customer found
            customer = customers.first()
            return JsonResponse({
                'success': True,
                'customer': {
                    'id': customer.id,
                    'name': customer.name,
                    'phone': customer.phone,
                    'email': customer.email or ''
                }
            })
        elif customers.count() > 1:
            # Multiple customers found
            customers_data = []
            for customer in customers:
                customers_data.append({
                    'id': customer.id,
                    'name': customer.name,
                    'phone': customer.phone,
                    'email': customer.email or ''
                })
            
            return JsonResponse({
                'success': True,
                'multiple': True,
                'customers': customers_data,
                'message': f'Found {customers.count()} customers with this phone number'
            })
        else:
            # No customer found
            return JsonResponse({
                'success': False,
                'message': 'No customer found with this phone number'
            })
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def get_variant_price(request):
    variant_id = request.GET.get('variant_id')
    if variant_id:
        try:
            variant = ProductVariant.objects.select_related('product').get(id=variant_id)
            return JsonResponse({
                'price': str(variant.effective_price),
                'stock': variant.quantity,
                'product_name': variant.product.name,
                'size': variant.size.name,
                'color': variant.color.name
            })
        except ProductVariant.DoesNotExist:
            pass
    return JsonResponse({'error': 'Variant not found'}, status=404)

@csrf_exempt
def get_product_variants(request):
    product_id = request.GET.get('product_id')
    if product_id:
        try:
            product = Product.objects.get(id=product_id)
            variants = ProductVariant.objects.filter(
                product=product, 
                quantity__gt=0
            ).select_related('size', 'color')
            
            variant_data = []
            for variant in variants:
                variant_data.append({
                    'id': variant.id,
                    'size': variant.size.name,
                    'color': variant.color.name,
                    'color_hex': variant.color.hex_code,
                    'quantity': variant.quantity,
                    'price': str(variant.effective_price),
                    'sku': variant.sku
                })
            
            return JsonResponse({'variants': variant_data})
        except Product.DoesNotExist:
            pass
    return JsonResponse({'error': 'Product not found'}, status=404)

def sales_report(request):
    """Enhanced sales report view with comprehensive statistics and filtering"""
    # Get date range from request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Base queryset
    bills = Bill.objects.select_related('customer').prefetch_related('items').order_by('-created_at')
    
    # Apply date filtering
    if start_date:
        bills = bills.filter(created_at__gte=start_date)
    if end_date:
        bills = bills.filter(created_at__lte=end_date)
    
    # Get filter parameters
    status_filter = request.GET.get('status')
    payment_filter = request.GET.get('payment_method')
    customer_filter = request.GET.get('customer')
    
    # Apply additional filters
    if status_filter:
        bills = bills.filter(status=status_filter)
    if payment_filter:
        bills = bills.filter(payment_method=payment_filter)
    if customer_filter:
        bills = bills.filter(customer__name__icontains=customer_filter)
    
    # Calculate comprehensive statistics with better error handling
    try:
        total_revenue = bills.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
        total_bills = bills.count()
        
        # Validate total_revenue to prevent infinity and negative values
        if total_revenue is None or total_revenue > Decimal('999999999') or total_revenue < Decimal('0'):
            total_revenue = Decimal('0')
        
        # Additional validation - check for abnormal values
        if total_bills == 0:
            total_revenue = Decimal('0')
        elif total_bills > 0:
            # Calculate average bill amount to detect anomalies
            avg_revenue_per_bill = total_revenue / total_bills
            if avg_revenue_per_bill > Decimal('1000000'):  # More than 1 lakh per bill is suspicious
                total_revenue = Decimal('0')
                
    except Exception as e:
        total_revenue = Decimal('0')
        total_bills = 0
    
    # Calculate total items sold using BillItem relationship
    total_items_sold = sum(bill.items.aggregate(count=Count('id'))['count'] or 0 for bill in bills)
    
    avg_bill_amount = total_revenue / total_bills if total_bills > 0 else Decimal('0')
    
    # Additional statistics with validation
    total_discount = bills.aggregate(total=Sum('discount_amount'))['total'] or Decimal('0')
    total_tax = bills.aggregate(total=Sum('tax_amount'))['total'] or Decimal('0')
    
    # Validate all monetary values to prevent infinity
    if total_revenue is None or total_revenue > Decimal('999999999') or total_revenue < Decimal('0'):
        total_revenue = Decimal('0')
    if total_discount is None or total_discount > Decimal('999999999') or total_discount < Decimal('0'):
        total_discount = Decimal('0')
    if total_tax is None or total_tax > Decimal('999999999') or total_tax < Decimal('0'):
        total_tax = Decimal('0')
    
    # Validate avg_bill_amount
    if avg_bill_amount is None or avg_bill_amount > Decimal('999999999') or avg_bill_amount < Decimal('0'):
        avg_bill_amount = Decimal('0')
    
    # Top customers by revenue with validation
    top_customers = bills.values('customer__name', 'customer__id').annotate(
        total_spent=Sum('total_amount'),
        bill_count=Count('id')
    ).order_by('-total_spent')[:10]
    
    # Validate top customers data
    validated_customers = []
    for customer in top_customers:
        if (customer['total_spent'] is not None and 
            customer['total_spent'] > 0 and 
            customer['total_spent'] < 999999999):
            validated_customers.append(customer)
    top_customers = validated_customers
    
    # Sales by payment method with validation
    payment_stats = bills.values('payment_method').annotate(
        count=Count('id'),
        total=Sum('total_amount')
    ).order_by('-total')
    
    # Validate payment stats
    validated_payment_stats = []
    for stat in payment_stats:
        if (stat['total'] is not None and 
            stat['total'] > 0 and 
            stat['total'] < 999999999):
            validated_payment_stats.append(stat)
    payment_stats = validated_payment_stats
    
    # Sales by status with validation
    status_stats = bills.values('status').annotate(
        count=Count('id'),
        total=Sum('total_amount')
    ).order_by('-total')
    
    # Validate status stats
    validated_status_stats = []
    for stat in status_stats:
        if (stat['total'] is not None and 
            stat['total'] > 0 and 
            stat['total'] < 999999999):
            validated_status_stats.append(stat)
    status_stats = validated_status_stats
    
    # Daily sales data for chart - fixed approach
    daily_sales = []
    
    # Get bills within last 30 days and group by date properly
    from datetime import datetime, timedelta
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_bills = bills.filter(created_at__gte=thirty_days_ago).order_by('created_at')
    
    # Group by date
    daily_data = {}
    for bill in recent_bills:
        if bill.total_amount and str(bill.total_amount) != 'inf' and isfinite(float(bill.total_amount)):
            date_str = bill.created_at.date().isoformat()
            if date_str not in daily_data:
                daily_data[date_str] = {'date': date_str, 'revenue': 0, 'count': 0}
            
            # Add validated amount
            amount = float(bill.total_amount)
            if amount > 0 and amount < 999999999:
                daily_data[date_str]['revenue'] += amount
                daily_data[date_str]['count'] += 1
    
    # Convert to sorted list
    daily_sales = sorted(daily_data.values(), key=lambda x: x['date'])
    
    # Monthly sales data for comparison
    monthly_sales = []  # Simplified for now
    
    # Top selling products with validation
    top_products = bills.values('items__product__name', 'items__product__id').annotate(
        total_quantity=Sum('items__quantity'),
        total_revenue=Sum('items__total')
    ).order_by('-total_quantity')[:10]
    
    # Validate top products data
    validated_products = []
    for product in top_products:
        if (product['total_revenue'] is not None and 
            product['total_revenue'] > 0 and 
            product['total_revenue'] < 999999999 and
            product['total_quantity'] is not None and
            product['total_quantity'] > 0):
            validated_products.append(product)
    top_products = validated_products
    
    # Hourly sales pattern - generate proper hourly data
    hourly_sales = []
    if bills.exists():
        # Group bills by hour
        hourly_data = {}
        for bill in bills:
            hour = bill.created_at.hour
            if hour not in hourly_data:
                hourly_data[hour] = {'hour': hour, 'revenue': 0, 'count': 0}
            
            # Validate bill amount before adding
            if bill.total_amount and str(bill.total_amount) != 'inf' and bill.total_amount > 0:
                hourly_data[hour]['revenue'] += float(bill.total_amount)
                hourly_data[hour]['count'] += 1
        
        # Convert to sorted list and fill missing hours with 0
        for hour in range(24):
            if hour in hourly_data:
                hourly_sales.append(hourly_data[hour])
            else:
                hourly_sales.append({'hour': hour, 'revenue': 0, 'count': 0})
    
    # Calculate growth metrics
    if start_date and end_date:
        from datetime import datetime, timedelta
        try:
            start = timezone.make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
            end = timezone.make_aware(datetime.strptime(end_date, '%Y-%m-%d'))
            days_diff = (end - start).days
            
            prev_start = start - timedelta(days=days_diff)
            prev_end = start - timedelta(days=1)
            
            prev_bills = Bill.objects.filter(
                created_at__date__gte=prev_start.date(),
                created_at__date__lte=prev_end.date()
            )
            
            prev_revenue = prev_bills.aggregate(total=Sum('total_amount'))['total'] or Decimal('0')
            prev_bills_count = prev_bills.count()
            
            # Validate previous revenue to prevent infinity and division by zero
            if prev_revenue is None or prev_revenue > Decimal('999999999') or prev_revenue < Decimal('0'):
                prev_revenue = Decimal('0')
            
            # Calculate growth only if we have valid data
            if prev_revenue > 0 and total_revenue > 0:
                revenue_growth = ((total_revenue - prev_revenue) / prev_revenue * 100)
                # Cap growth to reasonable values
                if revenue_growth > 999999 or revenue_growth < -999999:
                    revenue_growth = 0
            else:
                revenue_growth = 0
                
            if prev_bills_count > 0 and total_bills > 0:
                bills_growth = ((total_bills - prev_bills_count) / prev_bills_count * 100)
                # Cap growth to reasonable values
                if bills_growth > 999999 or bills_growth < -999999:
                    bills_growth = 0
            else:
                bills_growth = 0
        except:
            revenue_growth = 0
            bills_growth = 0
    else:
        revenue_growth = 0
        bills_growth = 0
    
    context = {
        'bills': bills,
        'total_revenue': total_revenue,
        'total_bills': total_bills,
        'total_items_sold': total_items_sold,
        'avg_bill_amount': avg_bill_amount,
        'total_discount': total_discount,
        'total_tax': total_tax,
        'top_customers': top_customers,
        'payment_stats': payment_stats,
        'status_stats': status_stats,
        'daily_sales': list(daily_sales),
        'monthly_sales': list(monthly_sales),
        'top_products': top_products,
        'hourly_sales': list(hourly_sales),
        'revenue_growth': round(revenue_growth, 2),
        'bills_growth': round(bills_growth, 2),
        'start_date': start_date,
        'end_date': end_date,
        'status_filter': status_filter,
        'payment_filter': payment_filter,
        'customer_filter': customer_filter,
        'bill_status_choices': Bill.STATUS_CHOICES,
        'payment_methods': Bill.PAYMENT_METHODS,
    }
    return render(request, 'shop/sales_report.html', context)

def get_sales_data(request):
    """API endpoint for sales chart data"""
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    bills = Bill.objects.order_by('-created_at')
    
    if start_date:
        bills = bills.filter(created_at__gte=start_date)
    if end_date:
        bills = bills.filter(created_at__lte=end_date)
    
    # Daily sales data
    daily_sales = bills.extra({
        'day': 'DATE(created_at)'
    }).values('day').annotate(
        revenue=Sum('total_amount'),
        count=Count('id')
    ).order_by('day')[:60]  # Last 60 days
    
    return JsonResponse({
        'daily_sales': list(daily_sales),
        'total_revenue': float(bills.aggregate(total=Sum('total_amount'))['total'] or 0),
        'total_bills': bills.count(),
    })

