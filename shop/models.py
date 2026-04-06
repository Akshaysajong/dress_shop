from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class Brand(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to='brand_logos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Size(models.Model):
    name = models.CharField(max_length=10, unique=True, help_text="Size name (S, M, L, XL, etc.)")
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    chest_measurement = models.CharField(max_length=20, blank=True, help_text="Chest measurement (e.g., 38-40)")
    length_measurement = models.CharField(max_length=20, blank=True, help_text="Length measurement")
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['order']

class Color(models.Model):
    name = models.CharField(max_length=50, unique=True)
    hex_code = models.CharField(max_length=7, default='#000000', help_text="Hex color code")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Material(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    care_instructions = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Product(models.Model):
    GENDER_CHOICES = [
        ('men', 'Men'),
        ('women', 'Women'),
        ('unisex', 'Unisex'),
        ('kids', 'Kids'),
    ]
    
    CATEGORY_CHOICES = [
        ('new', 'New'),
        ('old', 'Old'),
        ('trend', 'Trending'),
        ('clearance', 'Clearance'),
        ('limited', 'Limited Edition'),
    ]
    
    SEASON_CHOICES = [
        ('summer', 'Summer'),
        ('winter', 'Winter'),
        ('spring', 'Spring'),
        ('autumn', 'Autumn'),
        ('all_season', 'All Season'),
    ]
    
    OCCASION_CHOICES = [
        ('casual', 'Casual'),
        ('formal', 'Formal'),
        ('party', 'Party'),
        ('office', 'Office'),
        ('sports', 'Sports'),
        ('traditional', 'Traditional'),
    ]
    
    # Basic Information
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True)
    description = models.TextField(blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='brand')
    sku = models.CharField(max_length=50, unique=True, blank=True, help_text="Stock Keeping Unit")
    barcode = models.CharField(max_length=50, blank=True)
    
    # Categorization
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='new')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='unisex')
    season = models.CharField(max_length=10, choices=SEASON_CHOICES, blank=True)
    occasion = models.CharField(max_length=15, choices=OCCASION_CHOICES, blank=True)
    
    # Material and Quality
    materials = models.ManyToManyField(Material, blank=True)
    fabric_type = models.CharField(max_length=100, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Weight in grams")
    
    # Pricing
    base_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Base price")
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Selling price")
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, 
                                           validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Images
    main_image = models.ImageField(upload_to='products/main/', blank=True, null=True)
    
    # Inventory
    reorder_level = models.PositiveIntegerField(default=5, help_text="Reorder when stock reaches this level")
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_gender_display()})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            from django.utils.text import slugify
            import uuid
            
            # Generate base slug from name
            base_slug = slugify(self.name)
            slug = base_slug
            
            # Ensure uniqueness
            original_slug = slug
            counter = 1
            
            while Product.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1
            
            self.slug = slug
            
        if not self.sku:
            self.sku = f"PRD-{self.id:04d}" if self.id else "PRD-TEMP"
        super().save(*args, **kwargs)
    
    @property
    def effective_price(self):
        """Calculate effective price after discount"""
        if self.discount_percentage > 0:
            return self.selling_price * (Decimal('1') - (self.discount_percentage / Decimal('100')))
        return self.selling_price
    
    @property
    def total_stock(self):
        """Get total stock across all variants"""
        return self.variants.aggregate(total=models.Sum('quantity'))['total'] or 0
    
    class Meta:
        ordering = ['-created_at']

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    price_override = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, 
                                       help_text="Override product price if different")
    image = models.ImageField(upload_to='products/variants/', blank=True, null=True)
    sku = models.CharField(max_length=50, blank=True)
    
    def __str__(self):
        return f"{self.product.name} - {self.size.name} - {self.color.name}"
    
    def save(self, *args, **kwargs):
        if not self.sku:
            self.sku = f"{self.product.sku}-{self.size.name}-{self.color.name[:3].upper()}"
        super().save(*args, **kwargs)
    
    @property
    def effective_price(self):
        """Get price for this variant"""
        if self.price_override:
            if self.product.discount_percentage > 0:
                return self.price_override * (Decimal('1') - (self.product.discount_percentage / Decimal('100')))
            return self.price_override
        return self.product.effective_price
    
    class Meta:
        unique_together = ['product', 'size', 'color']

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return f"{self.product.name} - Image {self.order}"
    
    class Meta:
        ordering = ['order']

class Customer(models.Model):
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')], blank=True)
    loyalty_points = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Bill(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('net_banking', 'Net Banking'),
        ('wallet', 'Wallet'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    bill_number = models.CharField(max_length=50, unique=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='items')
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Bill'
        verbose_name_plural = 'Bills'
    
    def __str__(self):
        return self.bill_number
    
    def save(self, *args, **kwargs):
        # Only generate bill number if it's a new instance and doesn't have one
        if not self.pk and not self.bill_number:
            # Generate unique bill number
            from django.utils import timezone
            today_prefix = f"BILL-{timezone.now().strftime('%Y%m%d')}"
            
            # Get existing bills with today's prefix to find the next sequence
            existing_bills = Bill.objects.filter(bill_number__startswith=today_prefix).order_by('-bill_number')
            
            if existing_bills.exists():
                # Extract the sequence number from the latest bill
                try:
                    last_sequence = int(existing_bills.first().bill_number.split('-')[-1])
                    new_sequence = last_sequence + 1
                except (ValueError, IndexError):
                    new_sequence = 1
            else:
                new_sequence = 1
            
            self.bill_number = f"{today_prefix}-{new_sequence:04d}"
        
        super().save(*args, **kwargs)
    
    class Meta:
        ordering = ['-created_at']

class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='items')
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        product_name = self.product_variant.product.name if self.product_variant else self.product.name
        return f"{product_name} x {self.quantity}"

class StockAdjustment(models.Model):
    ADJUSTMENT_TYPES = [
        ('purchase', 'Purchase'),
        ('return', 'Return'),
        ('damage', 'Damage'),
        ('transfer', 'Transfer'),
        ('adjustment', 'Manual Adjustment'),
    ]
    
    product_variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    adjustment_type = models.CharField(max_length=15, choices=ADJUSTMENT_TYPES)
    quantity_before = models.IntegerField()
    quantity_after = models.IntegerField()
    quantity_changed = models.IntegerField()
    reason = models.TextField()
    created_by = models.CharField(max_length=200, blank=True)  # In real app, this would be User model
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        product_name = self.product_variant.product.name if self.product_variant else self.product.name
        return f"{product_name} - {self.adjustment_type} ({self.quantity_changed:+d})"
    
    class Meta:
        ordering = ['-created_at']
