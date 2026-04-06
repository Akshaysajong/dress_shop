# Dress Shop Management System

A Django-based web application for managing a dress selling shop with advanced stock management, billing, and dashboard functionality.

## Advanced Features

### Product Variants & Sizes
- Multiple variants per product (size + color combinations)
- Flexible size system with measurements
- Color management with hex codes
- Individual stock tracking per variant

### Brand & Material Management
- Brand categorization with logos
- Material tracking with care instructions
- Fabric type and weight specifications

### Advanced Categorization
- Gender-based categorization (Men, Women, Unisex, Kids)
- Season-based filtering (Summer, Winter, Spring, Autumn)
- Occasion-based categorization (Casual, Formal, Party, Office, Sports)
- Enhanced status categories (New, Old, Trending, Clearance, Limited Edition)

### Smart Pricing System
- Base price and selling price separation
- Dynamic discount percentages
- Price overrides per variant
- Effective price calculations

### Enhanced Dashboard
- Real-time statistics for products and variants
- Low stock alerts with visual indicators
- Featured products tracking
- Advanced filtering and search capabilities

### Stock Management
- Individual variant stock tracking
- Stock adjustment history
- Reorder level management
- Purchase, return, damage tracking

### Advanced Billing
- Multiple payment methods (Cash, Card, UPI, Net Banking, Wallet)
- Bill status management (Pending, Paid, Cancelled, Refunded)
- Tax and discount calculations
- Professional bill numbering system

### Customer Management
- Enhanced customer profiles with demographics
- Loyalty points system
- Purchase history tracking

### Image Management
- Product main images
- Variant-specific images
- Product image galleries
- Alt text and ordering support

## Dashboard Features

- **Real-time Statistics**: Products, variants, customers, bills
- **Stock Overview**: By category, gender, season, occasion
- **Low Stock Alerts**: Visual indicators for reordering
- **Recent Activity**: Latest bills and transactions
- **Top Products**: Best-selling items analysis
- **Featured Products**: Highlighted items management

## Stock Management Features

- **Variant Management**: Individual size/color combinations
- **Advanced Filtering**: Category, gender, brand, size, color, search
- **Bulk Operations**: Quick add/reduce stock with reasons
- **Stock History**: Complete adjustment tracking
- **Visual Indicators**: Color-coded stock levels
- **Reorder Management**: Automatic reorder level alerts

## Billing System Features

- **Variant Selection**: Choose specific size/color combinations
- **Dynamic Pricing**: Real-time price calculations
- **Stock Validation**: Prevent overselling
- **Payment Methods**: Multiple payment options
- **Professional Bills**: Clean, printable format
- **Customer Integration**: Automatic customer creation/lookup

## Modern UI Features

- **Responsive Design**: Mobile-friendly interface
- **Advanced Filtering**: Multi-parameter filtering
- **Interactive Elements**: Modals, tooltips, animations
- **Color Coding**: Visual status indicators
- **Search Functionality**: Product and bill search
- **Print Support**: Optimized bill printing

## Installation & Setup

### Quick Setup (Recommended)

1. **Navigate to the project directory:**
   ```bash
   cd dress_shop
   ```

2. **Run the setup script:**
   ```bash
   python setup.py
   ```
   
   This will automatically:
   - Create and apply migrations
   - Set up initial data (sizes, colors, materials, brands)
   - Create superuser
   - Start the development server

### Manual Setup

1. **Navigate to the project directory:**
   ```bash
   cd dress_shop
   ```

2. **Create and activate virtual environment:**
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install django
   ```

4. **Run migrations:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser:**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server:**
   ```bash
   python manage.py runserver
   ```

7. **Access the application:**
   - Main Application: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/

## Project Structure

```
dress_shop/
├── dress_shop/          # Main project directory
│   ├── settings.py      # Django settings
│   ├── urls.py          # Main URL configuration
│   └── wsgi.py          # WSGI configuration
├── shop/                # Main application
│   ├── models.py        # Enhanced database models
│   ├── views.py         # View functions with variants support
│   ├── urls.py          # App URL configuration
│   ├── admin.py         # Advanced admin configuration
│   └── templates/shop/  # Enhanced HTML templates
├── static/              # Static files (CSS, JS, images)
│   └── css/
│       └── style.css    # Custom styles
├── setup.py            # Automated setup script
└── manage.py            # Django management script
```

## Enhanced Database Models

### Core Models
- **Brand**: Brand management with logos and descriptions
- **Size**: Flexible size system with measurements
- **Color**: Color management with hex codes
- **Material**: Material tracking with care instructions

### Product Models
- **Product**: Enhanced product with categorization, pricing, images
- **ProductVariant**: Size/color combinations with individual stock
- **ProductImage**: Product image galleries

### Customer Models
- **Customer**: Enhanced customer profiles with demographics
- **Bill**: Advanced billing with payment methods and status
- **BillItem**: Line items with variant support
- **StockAdjustment**: Complete stock change tracking

## Getting Started

### 1. Access the Admin Panel
- Go to http://127.0.0.1:8000/admin/
- Login with your superuser credentials
- Create brands, sizes, colors, materials

### 2. Add Products
- Create products with detailed information
- Add variants for different sizes and colors
- Set pricing and upload images
- Configure categories and attributes

### 3. Manage Stock
- Use the dashboard to monitor stock levels
- Add/reduce stock with detailed reasons
- Track all adjustments in history
- Set reorder levels for automatic alerts

### 4. Create Bills
- Select specific product variants
- Automatic stock reduction on billing
- Choose payment methods
- Generate professional bills

### 5. Monitor Dashboard
- View real-time statistics
- Track low stock items
- Analyze sales trends
- Monitor customer activity

## Advanced Features Usage

### Product Variants
1. Create a product with basic information
2. Add multiple variants (size + color combinations)
3. Set individual stock levels per variant
4. Override prices for specific variants if needed

### Stock Adjustments
1. Go to Stock Management → Product List
2. Click "Add Stock" or "Reduce Stock" on variants
3. Enter quantity and reason
4. View complete adjustment history

### Advanced Filtering
1. Use multiple filters simultaneously
2. Filter by category, gender, brand, size, color
3. Search by product name, brand, or description
4. Save filter combinations for quick access

### Enhanced Billing
1. Select specific variants (not just products)
2. See real-time stock availability
3. Choose from multiple payment methods
4. Generate professional bills with automatic numbering

## Customization

### Adding New Categories
Edit `shop/models.py` and update the `CATEGORY_CHOICES` in the Product model:

```python
CATEGORY_CHOICES = [
    ('new', 'New'),
    ('old', 'Old'),
    ('trend', 'Trending'),
    ('clearance', 'Clearance'),
    ('limited', 'Limited Edition'),
    ('seasonal', 'Seasonal'),  # Add new category
]
```

### Custom Sizing
Add new sizes in the admin panel or through the setup script:

```python
sizes_data = [
    {'name': 'XXXL', 'order': 7, 'chest_measurement': '46-48', 'length_measurement': '32-33'},
    # Add more sizes as needed
]
```

### Payment Methods
Add new payment methods in the Bill model:

```python
PAYMENT_METHODS = [
    ('cash', 'Cash'),
    ('card', 'Card'),
    ('upi', 'UPI'),
    ('crypto', 'Cryptocurrency'),  # Add new method
]
```

## Security Notes

- Change `SECRET_KEY` in `dress_shop/settings.py` for production
- Set `DEBUG = False` in production
- Configure proper database settings for production
- Add authentication for the main application if needed
- Set up proper file permissions for media uploads

## Troubleshooting

### Common Issues
1. **Migration Errors**: Delete database and re-run setup script
2. **Static Files Not Loading**: Run `python manage.py collectstatic`
3. **Image Upload Issues**: Check media directory permissions
4. **Admin Access**: Ensure superuser was created correctly

### Getting Help
1. Check Django documentation: https://docs.djangoproject.com/
2. Review error logs in the terminal
3. Verify all migrations are applied correctly
4. Check model relationships and data integrity

## Performance Optimization

- Use database indexes for frequently queried fields
- Implement caching for dashboard statistics
- Optimize image sizes and formats
- Use pagination for large product lists
- Implement background tasks for heavy operations

## Updates & Maintenance

- Regularly run migrations for model updates
- Back up database before major changes
- Update Django and dependencies regularly
- Monitor disk space for media files
- Review and optimize slow queries

## Support

For issues or questions:
1. Check the Django documentation
2. Review the setup script output
3. Verify model relationships
4. Check browser console for JavaScript errors
5. Review Django error logs

## License

This project is open-source and available under the MIT License.
