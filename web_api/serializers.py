from rest_framework import serializers
from shop.models import Product, ProductVariant, ProductImage
from django.db.models import Min, Max, Sum
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta


class ProductImageSerializer(serializers.ModelSerializer):
    """Serializer for product images"""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ['id', 'url', 'is_primary', 'alt_text']
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class ProductVariantSerializer(serializers.ModelSerializer):
    """Serializer for product variants"""
    color_name = serializers.CharField(source='color.name', read_only=True)
    color_hex = serializers.CharField(source='color.hex_code', read_only=True)
    size_name = serializers.CharField(source='size.name', read_only=True)
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'sku', 'selling_price', 'price_override', 
            'effective_price', 'quantity', 'color_name', 
            'color_hex', 'size_name', 'image_url'
        ]
    
    def get_image_url(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class ProductListSerializer(serializers.ModelSerializer):
    """Advanced serializer for product list with all necessary fields"""
    brand_name = serializers.CharField(source='brand.name', read_only=True, allow_null=True)
    main_image_url = serializers.SerializerMethodField()
    price_range = serializers.SerializerMethodField()
    in_stock = serializers.SerializerMethodField()
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    base_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    selling_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    discount_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    is_new = serializers.SerializerMethodField()
    # images = ProductImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'gender', 'gender_display',
            'category', 'brand_name', 'base_price', 'selling_price', 
            'discount_percentage', 'main_image_url', 'is_featured', 'is_active',
            'is_new', 'price_range', 'in_stock', 'created_at'
        ]
    
    def get_main_image_url(self, obj):
        """Get main image URL with fallback to variant image"""
        request = self.context.get('request')
        
        # First try to get primary image from product images
        main_image = obj.images.filter(is_primary=True).first()
        if main_image and main_image.image:
            if request:
                return request.build_absolute_uri(main_image.image.url)
            return main_image.image.url
        
        # Fallback: try to get any image from product images
        any_image = obj.images.first()
        if any_image and any_image.image:
            if request:
                return request.build_absolute_uri(any_image.image.url)
            return any_image.image.url
        
        # Fallback: try product's main_image field (if it exists)
        if obj.main_image and hasattr(obj.main_image, 'url'):
            if request:
                return request.build_absolute_uri(obj.main_image.url)
            return obj.main_image.url
        
        # Final fallback: get image from first variant with image
        variant_with_image = obj.variants.exclude(image='').first()
        if variant_with_image and variant_with_image.image:
            if request:
                return request.build_absolute_uri(variant_with_image.image.url)
            return variant_with_image.image.url
        
        # No image found
        return None
    
    def get_price_range(self, obj):
        """Get price range from variants"""
        variants = obj.variants.filter(quantity__gt=0)
        if variants.exists():
            min_price = variants.aggregate(min_price=Min('price_override'))['min_price'] or 0
            max_price = variants.aggregate(max_price=Max('price_override'))['max_price'] or 0
            # If no price overrides, use selling_price
            if min_price == 0 and max_price == 0:
                min_price = obj.selling_price
                max_price = obj.selling_price
            return {
                'min': float(min_price),
                'max': float(max_price)
            }
        return {'min': 0, 'max': 0}
    
    def get_in_stock(self, obj):
        """Check if product has stock"""
        return obj.variants.filter(quantity__gt=0).exists()
    
    def get_is_new(self, obj):
        """Check if product is new (created within last 7 days)"""
        seven_days_ago = timezone.now() - timedelta(days=7)
        return obj.created_at > seven_days_ago


class ProductDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single product view"""
    brand_name = serializers.CharField(source='brand.name', read_only=True, allow_null=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    stock_info = serializers.SerializerMethodField()
    effective_price = serializers.SerializerMethodField()
    is_new = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'gender', 'gender_display',
            'category', 'brand_name', 'selling_price', 'effective_price',
            'discount_percentage', 'is_featured', 'is_active', 'is_new',
            'variants', 'images', 'stock_info', 'created_at', 'updated_at'
        ]
    
    def get_stock_info(self, obj):
        """Get detailed stock information"""
        variants = obj.variants.all()
        available_variants = [v for v in variants if v.quantity > 0]
        return {
            'total_variants': len(variants),
            'available_variants': len(available_variants),
            'total_quantity': sum(v.quantity for v in variants),
        }
    
    def get_effective_price(self, obj):
        """Calculate effective price after discount"""
        if obj.discount_percentage > 0:
            return float(obj.selling_price * (Decimal('1') - (obj.discount_percentage / Decimal('100'))))
        return float(obj.selling_price)
    
    def get_is_new(self, obj):
        """Check if product is new (created within last 7 days)"""
        seven_days_ago = timezone.now() - timedelta(days=7)
        return obj.created_at > seven_days_ago

