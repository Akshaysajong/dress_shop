from django.contrib import admin
from django.utils.html import format_html
from .models import (Brand, Size, Color, Material, Product, ProductVariant, ProductImage, 
                    Customer, Bill, BillItem, StockAdjustment)

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    ordering = ['name']

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name', 'order', 'chest_measurement', 'length_measurement']
    list_editable = ['order']
    ordering = ['order']

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ['name', 'color_display', 'created_at']
    search_fields = ['name']
    ordering = ['name']
    
    def color_display(self, obj):
        return format_html(
            '<span style="display: inline-block; width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc;"></span> {}',
            obj.hex_code, obj.hex_code
        )
    color_display.short_description = 'Color'

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ['name', 'created_at']
    search_fields = ['name']
    ordering = ['name']

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ['size', 'color', 'quantity', 'price_override', 'image', 'sku']
    ordering = ['size', 'color']

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'is_primary', 'order']
    ordering = ['order']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'gender', 'category', 'total_stock_display', 'effective_price_display', 'is_active', 'is_featured', 'created_at']
    list_filter = ['category', 'gender', 'brand', 'is_active', 'is_featured']
    search_fields = ['name', 'description', 'sku', 'brand__name']
    list_editable = ['is_active', 'is_featured']
    ordering = ['-created_at']
    inlines = [ProductVariantInline, ProductImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'brand', 'sku')
        }),
        ('Categorization', {
            'fields': ('category', 'gender')
        }),
        ('Material', {
            'fields': ('materials',)
        }),
        ('Pricing', {
            'fields': ('base_price', 'selling_price', 'discount_percentage')
        }),
        ('Images', {
            'fields': ('main_image',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured')
        }),
    )
    
    def total_stock_display(self, obj):
        total = obj.total_stock
        if total < 5:
            return format_html('<span style="color: red;">{}</span>', total)
        elif total < 20:
            return format_html('<span style="color: orange;">{}</span>', total)
        else:
            return format_html('<span style="color: green;">{}</span>', total)
    total_stock_display.short_description = 'Total Stock'
    
    def effective_price_display(self, obj):
        price = obj.effective_price
        if obj.discount_percentage > 0:
            return format_html('<span style="text-decoration: line-through; color: #999;">₹{}</span> ₹{}', 
                             obj.selling_price, price)
        return f'₹{price}'
    effective_price_display.short_description = 'Price'

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ['product_name', 'size', 'color', 'quantity', 'price_display', 'sku']
    list_filter = ['size', 'color', 'product__category', 'product__brand']
    search_fields = ['product__name', 'sku']
    list_editable = ['quantity']
    ordering = ['-product__created_at', 'size', 'color']
    
    def product_name(self, obj):
        return obj.product.name
    product_name.short_description = 'Product'
    
    def price_display(self, obj):
        price = obj.effective_price
        if obj.price_override:
            return format_html('<span style="color: blue;">₹{}</span>', price)
        return f'₹{price}'
    price_display.short_description = 'Price'

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'gender', 'loyalty_points', 'created_at']
    list_filter = ['gender', 'created_at']
    search_fields = ['name', 'phone', 'email']
    list_editable = ['loyalty_points']
    ordering = ['-created_at']

class BillItemInline(admin.TabularInline):
    model = BillItem
    extra = 1
    fields = ['product_variant', 'product', 'quantity', 'unit_price', 'discount_percentage', 'total']
    readonly_fields = ['total']

@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ['bill_number', 'customer', 'total_amount', 'payment_method', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['bill_number', 'customer__name']
    readonly_fields = ['bill_number', 'subtotal', 'discount_amount', 'tax_amount', 'total_amount']
    inlines = [BillItemInline]
    ordering = ['-created_at']
    
    fieldsets = (
        ('Bill Information', {
            'fields': ('customer', 'bill_number', 'status', 'payment_method')
        }),
        ('Amount Details', {
            'fields': ('subtotal', 'discount_amount', 'tax_amount', 'total_amount')
        }),
        ('Additional Information', {
            'fields': ('notes',)
        }),
    )

@admin.register(BillItem)
class BillItemAdmin(admin.ModelAdmin):
    list_display = ['bill_number', 'product_display', 'quantity', 'unit_price', 'discount_percentage', 'total']
    list_filter = ['bill__status', 'bill__payment_method']
    search_fields = ['bill__bill_number', 'product_variant__product__name', 'product__name']
    ordering = ['-bill__created_at']
    
    def bill_number(self, obj):
        return obj.bill.bill_number
    bill_number.short_description = 'Bill'
    
    def product_display(self, obj):
        if obj.product_variant:
            return f"{obj.product_variant.product.name} - {obj.product_variant.size.name} - {obj.product_variant.color.name}"
        return obj.product.name if obj.product else 'N/A'
    product_display.short_description = 'Product'

@admin.register(StockAdjustment)
class StockAdjustmentAdmin(admin.ModelAdmin):
    list_display = ['product_display', 'adjustment_type', 'quantity_before', 'quantity_after', 'quantity_changed_display', 'created_by', 'created_at']
    list_filter = ['adjustment_type', 'created_at']
    search_fields = ['product_variant__product__name', 'product__name', 'reason']
    ordering = ['-created_at']
    
    def product_display(self, obj):
        if obj.product_variant:
            return f"{obj.product_variant.product.name} - {obj.product_variant.size.name} - {obj.product_variant.color.name}"
        return obj.product.name if obj.product else 'N/A'
    product_display.short_description = 'Product'
    
    def quantity_changed_display(self, obj):
        if obj.quantity_changed > 0:
            return format_html('<span style="color: green;">+{}</span>', obj.quantity_changed)
        else:
            return format_html('<span style="color: red;">{}</span>', obj.quantity_changed)
    quantity_changed_display.short_description = 'Quantity Changed'
