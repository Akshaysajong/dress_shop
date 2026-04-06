# Fake Data Generation

This Django management command creates bulk fake product data for testing purposes.

## Usage

### Basic Usage (creates 50 products with 3 variants each):
```bash
python manage.py create_fake_data
```

### Custom Options:
```bash
# Create 100 products with 5 variants each and 3 images each
python manage.py create_fake_data --count 100 --variants 5 --images 3

# Create 25 products with 2 variants each
python manage.py create_fake_data --count 25 --variants 2
```

## What Gets Created

### Products
- Random product names (e.g., "Red T-Shirt", "Blue Jeans", "Green Sneakers")
- Random prices between ₹500 - ₹5000
- Random discounts (0-30%)
- Random categories and genders
- Random brands (Nike, Adidas, Puma, etc.)

### Variants
- Random sizes (XS, S, M, L, XL, XXL)
- Random colors (Red, Blue, Green, Black, etc.)
- Random stock levels (0-100 units)
- 30% chance of price override

### Images
- Placeholder images from picsum.photos
- First image marked as primary
- Multiple images per product

### Brands
- Creates 10 major brands if they don't exist
- Nike, Adidas, Puma, Reebok, etc.

## Example Output

```
Creating 50 products with 3 variants each...
Created 10 products...
Created 20 products...
Created 30 products...
Created 40 products...
Successfully created 50 products!
```

## Notes

- All products are set as `is_active=True`
- Random products are marked as `is_featured=True`
- Images use placeholder URLs (not actual files)
- SKUs are generated automatically (SKU-000001, SKU-000002, etc.)
- Stock levels determine variant availability
