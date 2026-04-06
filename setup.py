#!/usr/bin/env python
"""
Dress Shop Setup Script
This script helps set up the Django project with initial data and migrations.
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dress_shop.settings')
django.setup()

from django.core.management import execute_from_command_line
from shop.models import Brand, Size, Color, Material

def create_initial_data():
    """Create initial data for the dress shop"""
    
    # Create sizes
    sizes_data = [
        {'name': 'XS', 'order': 1, 'chest_measurement': '34-36', 'length_measurement': '26-27'},
        {'name': 'S', 'order': 2, 'chest_measurement': '36-38', 'length_measurement': '27-28'},
        {'name': 'M', 'order': 3, 'chest_measurement': '38-40', 'length_measurement': '28-29'},
        {'name': 'L', 'order': 4, 'chest_measurement': '40-42', 'length_measurement': '29-30'},
        {'name': 'XL', 'order': 5, 'chest_measurement': '42-44', 'length_measurement': '30-31'},
        {'name': 'XXL', 'order': 6, 'chest_measurement': '44-46', 'length_measurement': '31-32'},
    ]
    
    for size_data in sizes_data:
        size, created = Size.objects.get_or_create(name=size_data['name'])
        if created:
            size.order = size_data['order']
            size.chest_measurement = size_data['chest_measurement']
            size.length_measurement = size_data['length_measurement']
            size.save()
            print(f"Created size: {size.name}")
    
    # Create colors
    colors_data = [
        {'name': 'Black', 'hex_code': '#000000'},
        {'name': 'White', 'hex_code': '#FFFFFF'},
        {'name': 'Red', 'hex_code': '#FF0000'},
        {'name': 'Blue', 'hex_code': '#0000FF'},
        {'name': 'Green', 'hex_code': '#008000'},
        {'name': 'Yellow', 'hex_code': '#FFFF00'},
        {'name': 'Pink', 'hex_code': '#FFC0CB'},
        {'name': 'Purple', 'hex_code': '#800080'},
        {'name': 'Orange', 'hex_code': '#FFA500'},
        {'name': 'Brown', 'hex_code': '#A52A2A'},
        {'name': 'Gray', 'hex_code': '#808080'},
        {'name': 'Navy', 'hex_code': '#000080'},
    ]
    
    for color_data in colors_data:
        color, created = Color.objects.get_or_create(name=color_data['name'])
        if created:
            color.hex_code = color_data['hex_code']
            color.save()
            print(f"Created color: {color.name}")
    
    # Create materials
    materials_data = [
        {'name': 'Cotton', 'description': 'Soft, breathable fabric', 'care_instructions': 'Machine wash cold, tumble dry low'},
        {'name': 'Polyester', 'description': 'Durable synthetic fabric', 'care_instructions': 'Machine wash warm, do not bleach'},
        {'name': 'Silk', 'description': 'Luxurious natural fiber', 'care_instructions': 'Dry clean only'},
        {'name': 'Linen', 'description': 'Lightweight natural fabric', 'care_instructions': 'Machine wash cold, iron medium heat'},
        {'name': 'Wool', 'description': 'Warm natural fiber', 'care_instructions': 'Hand wash cold, dry flat'},
        {'name': 'Denim', 'description': 'Durable cotton fabric', 'care_instructions': 'Machine wash cold, tumble dry medium'},
        {'name': 'Rayon', 'description': 'Semi-synthetic fabric', 'care_instructions': 'Machine wash cold, gentle cycle'},
    ]
    
    for material_data in materials_data:
        material, created = Material.objects.get_or_create(name=material_data['name'])
        if created:
            material.description = material_data['description']
            material.care_instructions = material_data['care_instructions']
            material.save()
            print(f"Created material: {material.name}")
    
    # Create brands
    brands_data = [
        {'name': 'Fashion Hub', 'description': 'Trendy fashion brand'},
        {'name': 'Classic Wear', 'description': 'Timeless fashion pieces'},
        {'name': 'Urban Style', 'description': 'Modern urban fashion'},
        {'name': 'Elegance', 'description': 'Premium fashion brand'},
    ]
    
    for brand_data in brands_data:
        brand, created = Brand.objects.get_or_create(name=brand_data['name'])
        if created:
            brand.description = brand_data['description']
            brand.save()
            print(f"Created brand: {brand.name}")

def main():
    """Main setup function"""
    print("🚀 Setting up Dress Shop Management System...")
    
    # Create necessary directories
    print("\n📁 Creating directories...")
    directories = [
        'media/products/main',
        'media/products/variants', 
        'media/products/gallery',
        'media/brand_logos',
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Run migrations
    print("\n📋 Running migrations...")
    try:
        execute_from_command_line(['manage.py', 'makemigrations'])
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations completed successfully!")
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return
    
    # Create initial data
    print("\n📦 Creating initial data...")
    create_initial_data()
    print("✅ Initial data created successfully!")
    
    # Create superuser prompt
    print("\n👤 Creating superuser...")
    try:
        execute_from_command_line(['manage.py', 'createsuperuser'])
    except SystemExit:
        # User cancelled superuser creation
        pass
    
    print("\n🎉 Setup completed successfully!")
    print("\nNext steps:")
    print("1. Run the development server: python manage.py runserver")
    print("2. Open your browser to: http://127.0.0.1:8000/")
    print("3. Access admin panel at: http://127.0.0.1:8000/admin/")
    print("4. Add products and variants using the admin panel")
    print("5. Start using the shop management system!")

if __name__ == '__main__':
    main()
