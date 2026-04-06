# Home API Documentation

## Overview

The Home API provides comprehensive data for the home page of the Dress Shop mobile application. It includes featured products, new arrivals, categories, brands, dashboard statistics, recent bills, and top products.

## Base URL

```
Development: http://localhost:8000/api/
Production: https://your-domain.com/api/
```

## Endpoints

### 1. Home API (Complete Data)

**GET /api/home/**

Returns comprehensive home page data including all components.

#### Response Example:
```json
{
    "success": true,
    "message": "Home data retrieved successfully",
    "data": {
        "featured_products": [
            {
                "id": 1,
                "name": "Summer Dress",
                "slug": "summer-dress",
                "category": "dress",
                "gender": "women",
                "brand_name": "Fashion Brand",
                "price_range": {
                    "min": 29.99,
                    "max": 49.99
                },
                "image_url": "http://example.com/media/products/dress1.jpg",
                "is_featured": true,
                "discount_percentage": 10.0,
                "in_stock": true
            }
        ],
        "new_arrivals": [
            {
                "id": 2,
                "name": "Winter Coat",
                "slug": "winter-coat",
                "category": "coat",
                "gender": "women",
                "brand_name": "Winter Brand",
                "price_range": {
                    "min": 89.99,
                    "max": 129.99
                },
                "image_url": "http://example.com/media/products/coat1.jpg",
                "is_featured": false,
                "discount_percentage": 0.0,
                "in_stock": true
            }
        ],
        "categories": ["dress", "shirt", "pants", "coat", "accessories"],
        "brands": ["Fashion Brand", "Winter Brand", "Sports Brand"],
        "stats": {
            "total_revenue": 1250.75,
            "total_bills": 25,
            "total_customers": 15,
            "total_products": 8
        },
        "recent_bills": [
            {
                "id": 1,
                "bill_number": "BILL-20240101-0001",
                "customer_name": "John Doe",
                "total_amount": 59.99,
                "status": "paid",
                "created_at": "2024-01-01T12:00:00Z"
            }
        ],
        "top_products": [
            {
                "name": "Summer Dress",
                "total_quantity": 12,
                "total_revenue": 359.88
            }
        ]
    }
}
```

### 2. Featured Products

**GET /api/home/featured/**

Returns featured products only.

#### Query Parameters:
- `limit` (int, optional): Number of products to return (default: 8)

#### Example Request:
```
GET /api/home/featured/?limit=5
```

#### Response Example:
```json
{
    "success": true,
    "message": "Featured products retrieved successfully",
    "data": {
        "featured_products": [
            {
                "id": 1,
                "name": "Summer Dress",
                "slug": "summer-dress",
                "category": "dress",
                "gender": "women",
                "brand_name": "Fashion Brand",
                "price_range": {
                    "min": 29.99,
                    "max": 49.99
                },
                "image_url": "http://example.com/media/products/dress1.jpg",
                "is_featured": true,
                "discount_percentage": 10.0,
                "in_stock": true
            }
        ]
    }
}
```

### 3. New Arrivals

**GET /api/home/new-arrivals/**

Returns new arrival products only.

#### Query Parameters:
- `limit` (int, optional): Number of products to return (default: 8)
- `days` (int, optional): Number of days to consider as "new" (default: 30)

#### Example Request:
```
GET /api/home/new-arrivals/?limit=5&days=7
```

#### Response Example:
```json
{
    "success": true,
    "message": "New arrivals retrieved successfully",
    "data": {
        "new_arrivals": [
            {
                "id": 2,
                "name": "Winter Coat",
                "slug": "winter-coat",
                "category": "coat",
                "gender": "women",
                "brand_name": "Winter Brand",
                "price_range": {
                    "min": 89.99,
                    "max": 129.99
                },
                "image_url": "http://example.com/media/products/coat1.jpg",
                "is_featured": false,
                "discount_percentage": 0.0,
                "in_stock": true
            }
        ]
    }
}
```

### 4. Categories

**GET /api/home/categories/**

Returns available product categories.

#### Response Example:
```json
{
    "success": true,
    "message": "Categories retrieved successfully",
    "data": {
        "categories": ["dress", "shirt", "pants", "coat", "accessories"]
    }
}
```

### 5. Brands

**GET /api/home/brands/**

Returns available product brands.

#### Response Example:
```json
{
    "success": true,
    "message": "Brands retrieved successfully",
    "data": {
        "brands": ["Fashion Brand", "Winter Brand", "Sports Brand"]
    }
}
```

## Data Models

### Product Fields

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Product ID |
| name | string | Product name |
| slug | string | URL-friendly slug |
| category | string | Product category |
| gender | string | Target gender (men/women/unisex) |
| brand_name | string | Brand name |
| price_range | object | Min/max price range |
| image_url | string | Product image URL |
| is_featured | boolean | Whether product is featured |
| discount_percentage | float | Discount percentage |
| in_stock | boolean | Whether product is in stock |

### Stats Fields

| Field | Type | Description |
|-------|------|-------------|
| total_revenue | float | Total revenue from all bills |
| total_bills | integer | Total number of bills |
| total_customers | integer | Total number of customers |
| total_products | integer | Total number of active products |

### Recent Bill Fields

| Field | Type | Description |
|-------|------|-------------|
| id | integer | Bill ID |
| bill_number | string | Bill number |
| customer_name | string | Customer name |
| total_amount | float | Total bill amount |
| status | string | Bill status (paid/pending/cancelled) |
| created_at | string | Creation timestamp (ISO 8601) |

### Top Product Fields

| Field | Type | Description |
|-------|------|-------------|
| name | string | Product name |
| total_quantity | integer | Total quantity sold |
| total_revenue | float | Total revenue from this product |

## Mobile App Integration

### Flutter/Dart Example

```dart
class HomeService {
  final String baseUrl = 'http://localhost:8000/api';

  Future<Map<String, dynamic>> getHomeData() async {
    final response = await http.get(Uri.parse('$baseUrl/home/'));
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to load home data');
    }
  }

  Future<Map<String, dynamic>> getFeaturedProducts({int limit = 8}) async {
    final response = await http.get(Uri.parse('$baseUrl/home/featured/?limit=$limit'));
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Failed to load featured products');
    }
  }
}
```

### React Native Example

```javascript
class HomeService {
  baseUrl = 'http://localhost:8000/api';

  async getHomeData() {
    try {
      const response = await fetch(`${this.baseUrl}/home/`);
      const data = await response.json();
      
      if (response.ok) {
        return data;
      } else {
        throw new Error('Failed to load home data');
      }
    } catch (error) {
      console.error('Home API Error:', error);
      throw error;
    }
  }

  async getFeaturedProducts(limit = 8) {
    try {
      const response = await fetch(`${this.baseUrl}/home/featured/?limit=${limit}`);
      const data = await response.json();
      
      if (response.ok) {
        return data;
      } else {
        throw new Error('Failed to load featured products');
      }
    } catch (error) {
      console.error('Featured Products API Error:', error);
      throw error;
    }
  }
}
```

## Error Handling

All endpoints return consistent error responses:

```json
{
    "success": false,
    "message": "Internal server error",
    "error": "Detailed error message"
}
```

### Common HTTP Status Codes

- `200` - Success
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

## Performance Considerations

1. **Image URLs**: All image URLs are absolute and include the full domain
2. **Pagination**: Featured products and new arrivals support limit parameter
3. **Caching**: Consider implementing client-side caching for categories and brands
4. **Lazy Loading**: Load individual components separately for better performance

## Testing

### cURL Examples

```bash
# Get complete home data
curl http://localhost:8000/api/home/

# Get featured products with limit
curl http://localhost:8000/api/home/featured/?limit=5

# Get new arrivals from last 7 days
curl http://localhost:8000/api/home/new-arrivals/?days=7

# Get categories
curl http://localhost:8000/api/home/categories/

# Get brands
curl http://localhost:8000/api/home/brands/
```

### Postman Collection

You can import these endpoints into Postman for testing:

1. Create a new collection called "Dress Shop Home API"
2. Add the following requests:
   - GET Home Data: `/api/home/`
   - GET Featured Products: `/api/home/featured/`
   - GET New Arrivals: `/api/home/new-arrivals/`
   - GET Categories: `/api/home/categories/`
   - GET Brands: `/api/home/brands/`

## Future Enhancements

1. **Personalization**: Add user-specific recommendations
2. **Filters**: Add category and brand filters to products
3. **Sorting**: Add sorting options for products
4. **Search**: Add search functionality within home data
5. **Analytics**: Track which products are viewed most from home page
