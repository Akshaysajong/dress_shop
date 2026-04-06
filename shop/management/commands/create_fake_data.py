from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from shop.models import Product, ProductVariant, ProductImage, Brand, Size, Color, Material
from decimal import Decimal
import random
import string

User = get_user_model()

class Command(BaseCommand):
    help = 'Create bulk fake product data for testing without errors'

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=500, help='Number of products to create')
        parser.add_argument('--variants', type=int, default=3, help='Number of variants per product')
        parser.add_argument('--images', type=int, default=2, help='Number of images per product')
        parser.add_argument('--batch-size', type=int, default=50, help='Batch size for processing')

    def handle(self, *args, **options):
        count = options['count']
        variants_count = options['variants']
        images_count = options['images']
        batch_size = options['batch_size']
        
        # Check existing data first
        existing_products = Product.objects.count()
        existing_variants = ProductVariant.objects.count()
        existing_images = ProductImage.objects.count()
        
        self.stdout.write(f'Existing data: {existing_products} products, {existing_variants} variants, {existing_images} images')
        self.stdout.write(f'Creating {count} additional products with {variants_count} variants each...')
        
        try:
            with transaction.atomic():
                # Create base data first
                self.stdout.write('Creating base data (sizes, colors, brands, materials)...')
                sizes = self.create_sizes()
                colors = self.create_colors()
                brands = self.create_brands()
                materials = self.create_materials()
                
                # Create products in batches to avoid memory issues
                created_count = 0
                skipped_count = 0
                
                for batch_start in range(0, count, batch_size):
                    batch_end = min(batch_start + batch_size, count)
                    batch_products = []
                    
                    for i in range(batch_start, batch_end):
                        product_index = existing_products + i + 1  # Start from existing count
                        product = self.create_product(product_index, brands, materials, i)
                        if product:
                            batch_products.append(product)
                            created_count += 1
                        else:
                            skipped_count += 1
                    
                    # Create variants and images for batch
                    for product in batch_products:
                        self.create_variants(product, variants_count, sizes, colors)
                        self.create_images(product, images_count)
                    
                    self.stdout.write(f'Batch {batch_start//batch_size + 1}: Created {len(batch_products)} products...')
                
                # Final summary
                total_products = Product.objects.count()
                total_variants = ProductVariant.objects.count()
                total_images = ProductImage.objects.count()
                
                self.stdout.write(self.style.SUCCESS(f'SUCCESS!'))
                self.stdout.write(self.style.SUCCESS(f'  Created: {created_count} new products'))
                self.stdout.write(self.style.SUCCESS(f'  Skipped: {skipped_count} products (due to conflicts)'))
                self.stdout.write(self.style.SUCCESS(f'  Total Products: {total_products}'))
                self.stdout.write(self.style.SUCCESS(f'  Total Variants: {total_variants}'))
                self.stdout.write(self.style.SUCCESS(f'  Total Images: {total_images}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating products: {str(e)}'))
            raise

    def create_sizes(self):
        """Create sizes if they don't exist"""
        size_data = [
            ('XS', 'Extra Small', 0),
            ('S', 'Small', 1),
            ('M', 'Medium', 2),
            ('L', 'Large', 3),
            ('XL', 'Extra Large', 4),
            ('XXL', 'Double Extra Large', 5),
        ]
        sizes = []
        
        for name, chest, order in size_data:
            size, created = Size.objects.get_or_create(
                name=name,
                defaults={
                    'chest_measurement': chest,
                    'order': order
                }
            )
            sizes.append(size)
        
        return sizes

    def create_colors(self):
        """Create colors if they don't exist"""
        color_data = [
            ('Red', '#FF0000'),
            ('Blue', '#0000FF'),
            ('Green', '#00FF00'),
            ('Black', '#000000'),
            ('White', '#FFFFFF'),
            ('Gray', '#808080'),
            ('Navy', '#000080'),
            ('Brown', '#A52A2A'),
            ('Purple', '#800080'),
            ('Orange', '#FFA500'),
            ('Pink', '#FFC0CB'),
            ('Yellow', '#FFFF00'),
            ('Cyan', '#00FFFF'),
            ('Magenta', '#FF00FF'),
        ]
        colors = []
        
        for name, hex_code in color_data:
            color, created = Color.objects.get_or_create(
                name=name,
                defaults={
                    'hex_code': hex_code
                }
            )
            colors.append(color)
        
        return colors

    def create_materials(self):
        """Create materials if they don't exist"""
        material_names = [
            'Cotton', 'Polyester', 'Wool', 'Denim', 'Leather', 
            'Synthetic', 'Fleece', 'Linen', 'Rayon', 'Spandex',
            'Silk', 'Velvet', 'Chiffon', 'Satin', 'Nylon'
        ]
        materials = []
        
        for name in material_names:
            material, created = Material.objects.get_or_create(
                name=name,
                defaults={
                    'description': f'{name} material for clothing'
                }
            )
            materials.append(material)
        
        return materials

    def create_brands(self):
        """Create brands if they don't exist"""
        brand_data = [
            ('Nike', 'Leading sportswear brand'),
            ('Adidas', 'German sportswear company'),
            ('Puma', 'German multinational company'),
            ('Reebok', 'British footwear company'),
            ('Under Armour', 'American sports equipment company'),
            ('New Balance', 'American footwear company'),
            ('ASICS', 'Japanese multinational corporation'),
            ('Skechers', 'American footwear company'),
            ('Fila', 'South Korean footwear company'),
            ('Converse', 'American shoe company'),
            ('Vans', 'American manufacturer of skateboarding shoes'),
            ('Tommy Hilfiger', 'American clothing company'),
            ('Calvin Klein', 'American fashion house'),
            ('Ralph Lauren', 'American fashion company'),
            ('Gap', 'American clothing retailer'),
        ]
        brands = []
        
        for name, description in brand_data:
            brand, created = Brand.objects.get_or_create(
                name=name,
                defaults={
                    'description': description,
                    
                }
            )
            brands.append(brand)
        
        return brands

    def create_product(self, index, brands, materials, i):
        """Create a single product with proper error handling"""
        try:
            genders = ['men', 'women', 'unisex', 'kids']
            categories = ['new', 'trending', 'limited', 'clearance']
            product_types = [
                'T-Shirt', 'Jeans', 'Sneakers', 'Jacket', 'Shorts', 'Sweater', 
                'Hoodie', 'Polo', 'Tank Top', 'Cardigan', 'Dress', 'Skirt', 
                'Blazer', 'Coat', 'Vest', 'Pants', 'Leggings', 'Sports Bra'
            ]
            
            # Generate unique product data with more variety
            colors = ['Red', 'Blue', 'Green', 'Black', 'White', 'Gray', 'Navy', 'Brown', 'Purple', 'Orange', 'Pink', 'Yellow', 'Cyan', 'Magenta']
            product_type = random.choice(product_types)
            color = random.choice(colors)
            
            # Create unique name to avoid duplicates
            name = f"{color} {product_type} #{index}"
            
            # Create unique slug
            slug = f"{color.lower()}-{product_type.lower().replace(' ', '-')}-{index}"
            
            # Ensure slug is unique
            counter = 1
            original_slug = slug
            while Product.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1
            
            # Ensure name is unique
            name_counter = 1
            original_name = name
            while Product.objects.filter(name=name).exists():
                name = f"{original_name}-{name_counter}"
                name_counter += 1
            
            description = f"High-quality {color.lower()} {product_type.lower()} made from premium materials. Perfect for casual wear and sports activities. Product #{index}."
            gender = random.choice(genders)
            category = random.choice(categories)
            brand = random.choice(brands)
            
            # Random prices
            base_price = Decimal(random.uniform(500, 5000)).quantize(Decimal('0.01'))
            selling_price = base_price * Decimal(random.uniform(0.8, 0.95)).quantize(Decimal('0.01'))
            discount_percentage = round(float(base_price - selling_price) / float(base_price) * 100, 2)
            
            # Create product with all required fields
            product = Product.objects.create(
                name=name,
                slug=slug,
                description=description,
                gender=gender,
                category=category,
                brand=brand,
                base_price=base_price,
                selling_price=selling_price,
                discount_percentage=discount_percentage,
                is_featured=random.choice([True, False]),
                is_active=True,
                sku=f"SKU-{index:04d}",
                weight=random.randint(100, 500),
                fabric_type=random.choice(['Cotton', 'Polyester', 'Wool', 'Denim', 'Leather']),
                occasion=random.choice(['Casual', 'Sports', 'Formal', 'Party']),
                season=random.choice(['Summer', 'Winter', 'Spring', 'Fall']),
                reorder_level=random.randint(5, 20),
                main_image="products/main/91sQs51s6kL_SzKBI9w._AC_UY1100_.jpg"
            )
            
            # Add materials to product (many-to-many)
            selected_materials = random.sample(materials, random.randint(1, 3))
            product.materials.set(selected_materials)
            
            return product
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Error creating product {index}: {str(e)}'))
            return None

    def create_variants(self, product, count, sizes, colors):
        """Create variants for a product with proper error handling"""
        try:
            # Create unique combinations to avoid duplicates
            used_combinations = set()
            created_variants = 0
            
            while created_variants < count and len(used_combinations) < len(sizes) * len(colors):
                size = random.choice(sizes)
                color = random.choice(colors)
                combination = (size.id, color.id)
                
                if combination not in used_combinations:
                    used_combinations.add(combination)
                    
                    # Price override (sometimes higher, sometimes lower)
                    price_override = None
                    if random.random() > 0.7:  # 30% chance of price override
                        base_price = product.selling_price
                        multiplier = Decimal(random.uniform(0.9, 1.2))
                        price_override = (base_price * multiplier).quantize(Decimal('0.01'))
                    
                    # Random quantity
                    quantity = random.randint(0, 100)
                    
                    # Create variant with unique SKU
                    sku = f"{product.sku}-{size.name}-{color.name[:3].upper()}"
                    
                    # Ensure SKU is unique
                    counter = 1
                    original_sku = sku
                    while ProductVariant.objects.filter(sku=sku).exists():
                        sku = f"{original_sku}-{counter}"
                        counter += 1
                    
                    ProductVariant.objects.create(
                        product=product,
                        size=size,
                        color=color,
                        sku=sku,
                        price_override=price_override,
                        quantity=quantity
                    )
                    created_variants += 1
                    
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Error creating variants for product {product.name}: {str(e)}'))

    def create_images(self, product, count):
        """Create images for a product"""
        try:
            # Use placeholder images with different seeds
            for i in range(count):
                # Use a variety of placeholder image URLs
                image_seeds = [
                    "products/main/A1-LacgWLYL._AC_UY1100_.jpg",
                    "products/main/sports-wear.jpg",
                    "products/main/fashion-item.jpg",
                    "products/main/clothing-item.jpg",
                    "products/main/apparel-product.jpg"
                ]
                
                image_url = random.choice(image_seeds)
                
                ProductImage.objects.create(
                    product=product,
                    image=image_url,
                    is_primary=(i == 0),  # First image is primary
                    alt_text=f"{product.name} - View {i+1}",
                    order=i
                )
                    
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Error creating images for product {product.name}: {str(e)}'))
