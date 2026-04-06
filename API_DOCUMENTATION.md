# Dress Shop Mobile API Documentation

## Overview

This document provides comprehensive API documentation for the Dress Shop mobile application. The API is built using Django REST Framework with JWT authentication.

## Base URL

```
Development: http://localhost:8000/api/
Production: https://your-domain.com/api/
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Token Endpoints

#### POST /api/auth/login/
Login user and return JWT tokens.

**Request Body:**
```json
{
    "username": "your_username",
    "password": "your_password"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Login successful",
    "data": {
        "user": {
            "id": 1,
            "username": "your_username",
            "email": "user@example.com",
            "first_name": "John",
            "last_name": "Doe"
        },
        "tokens": {
            "refresh": "refresh_token_here",
            "access": "access_token_here"
        }
    }
}
```

#### POST /api/auth/register/
Register a new user.

**Request Body:**
```json
{
    "username": "new_user",
    "email": "newuser@example.com",
    "password": "secure_password",
    "first_name": "Jane",
    "last_name": "Smith"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Registration successful",
    "data": {
        "user": {
            "id": 2,
            "username": "new_user",
            "email": "newuser@example.com",
            "first_name": "Jane",
            "last_name": "Smith"
        },
        "tokens": {
            "refresh": "refresh_token_here",
            "access": "access_token_here"
        }
    }
}
```

#### POST /api/auth/logout/
Logout user (client-side token removal).

**Response:**
```json
{
    "success": true,
    "message": "Logout successful"
}
```

#### GET /api/auth/profile/
Get current user profile.

**Response:**
```json
{
    "success": true,
    "data": {
        "user": {
            "id": 1,
            "username": "your_username",
            "email": "user@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "date_joined": "2024-01-01T12:00:00Z"
        }
    }
}
```

## Products API

### GET /api/products/
Get list of products with pagination and filtering.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20)
- `category` (string): Filter by category
- `gender` (string): Filter by gender
- `search` (string): Search in name, description, brand
- `sort_by` (string): Sort by field (name, price, created_at)
- `sort_order` (string): Sort order (asc, desc)

**Example Request:**
```
GET /api/products/?page=1&limit=10&category=dress&search=cotton&sort_by=price&sort_order=asc
```

**Response:**
```json
{
    "success": true,
    "data": {
        "products": [
            {
                "id": 1,
                "name": "Cotton Summer Dress",
                "slug": "cotton-summer-dress",
                "description": "Comfortable cotton dress for summer...",
                "category": "dress",
                "gender": "women",
                "brand": "Fashion Brand",
                "price_range": {
                    "min": 29.99,
                    "max": 49.99
                },
                "image": "http://example.com/media/products/dress1.jpg",
                "is_featured": true,
                "discount_percentage": 10.0,
                "created_at": "2024-01-01T12:00:00Z"
            }
        ],
        "pagination": {
            "current_page": 1,
            "total_pages": 5,
            "total_items": 47,
            "items_per_page": 10,
            "has_next": true,
            "has_prev": false
        }
    }
}
```

### GET /api/products/{id}/
Get detailed product information.

**Response:**
```json
{
    "success": true,
    "data": {
        "product": {
            "id": 1,
            "name": "Cotton Summer Dress",
            "slug": "cotton-summer-dress",
            "description": "Full product description...",
            "category": "dress",
            "gender": "women",
            "brand": "Fashion Brand",
            "price_range": {
                "min": 29.99,
                "max": 49.99
            },
            "discount_percentage": 10.0,
            "is_featured": true,
            "is_active": true,
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z"
        },
        "variants": [
            {
                "id": 1,
                "sku": "DRESS-001-S-BLUE",
                "size": "S",
                "color": {
                    "name": "Blue",
                    "hex_code": "#0000FF"
                },
                "selling_price": 29.99,
                "price_override": null,
                "effective_price": 26.99,
                "quantity": 10,
                "is_available": true,
                "image": "http://example.com/media/variants/dress1_s_blue.jpg"
            }
        ],
        "images": [
            {
                "id": 1,
                "url": "http://example.com/media/products/dress1_1.jpg",
                "is_main": true,
                "alt_text": "Cotton Summer Dress - Front View"
            }
        ],
        "materials": [
            {"name": "Cotton"},
            {"name": "Spandex"}
        ],
        "stock_info": {
            "total_variants": 6,
            "available_variants": 4,
            "total_quantity": 35
        }
    }
}
```

## Customers API

### GET /api/customers/
Get list of customers with pagination and search.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20)
- `search` (string): Search in name, phone, email

**Response:**
```json
{
    "success": true,
    "data": {
        "customers": [
            {
                "id": 1,
                "name": "John Doe",
                "phone": "+1234567890",
                "email": "john@example.com",
                "address": "123 Main St, City, State",
                "total_bills": 5,
                "total_spent": 299.95,
                "created_at": "2024-01-01T12:00:00Z"
            }
        ],
        "pagination": {
            "current_page": 1,
            "total_pages": 3,
            "total_items": 25,
            "items_per_page": 20,
            "has_next": true,
            "has_prev": false
        }
    }
}
```

### POST /api/customers/
Create a new customer.

**Request Body:**
```json
{
    "name": "Jane Smith",
    "phone": "+1234567891",
    "email": "jane@example.com",
    "address": "456 Oak Ave, City, State"
}
```

**Response:**
```json
{
    "success": true,
    "message": "Customer created successfully",
    "data": {
        "customer": {
            "id": 2,
            "name": "Jane Smith",
            "phone": "+1234567891",
            "email": "jane@example.com",
            "address": "456 Oak Ave, City, State",
            "created_at": "2024-01-01T12:00:00Z"
        }
    }
}
```

### GET /api/customers/{id}/
Get customer details with bills.

**Response:**
```json
{
    "success": true,
    "data": {
        "customer": {
            "id": 1,
            "name": "John Doe",
            "phone": "+1234567890",
            "email": "john@example.com",
            "address": "123 Main St, City, State",
            "total_bills": 5,
            "total_spent": 299.95,
            "created_at": "2024-01-01T12:00:00Z"
        },
        "bills": [
            {
                "id": 1,
                "bill_number": "BILL-20240101-0001",
                "total_amount": 59.99,
                "status": "paid",
                "payment_method": "cash",
                "created_at": "2024-01-01T12:00:00Z"
            }
        ]
    }
}
```

### PUT /api/customers/{id}/
Update customer information.

**Request Body:**
```json
{
    "name": "John Updated",
    "email": "johnupdated@example.com",
    "address": "789 New St, City, State"
}
```

### DELETE /api/customers/{id}/
Delete a customer.

**Response:**
```json
{
    "success": true,
    "message": "Customer deleted successfully"
}
```

## Bills API

### GET /api/bills/
Get list of bills with filtering and pagination.

**Query Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20)
- `status` (string): Filter by status (paid, pending, cancelled)
- `payment_method` (string): Filter by payment method
- `customer_id` (int): Filter by customer ID
- `search` (string): Search in bill number, customer name/phone
- `start_date` (string): Filter by start date (YYYY-MM-DD)
- `end_date` (string): Filter by end date (YYYY-MM-DD)

**Response:**
```json
{
    "success": true,
    "data": {
        "bills": [
            {
                "id": 1,
                "bill_number": "BILL-20240101-0001",
                "customer": {
                    "id": 1,
                    "name": "John Doe",
                    "phone": "+1234567890"
                },
                "subtotal": 59.99,
                "discount_amount": 0.0,
                "tax_amount": 0.0,
                "total_amount": 59.99,
                "status": "paid",
                "payment_method": "cash",
                "created_at": "2024-01-01T12:00:00Z"
            }
        ],
        "pagination": {
            "current_page": 1,
            "total_pages": 2,
            "total_items": 15,
            "items_per_page": 20,
            "has_next": true,
            "has_prev": false
        }
    }
}
```

### POST /api/bills/
Create a new bill.

**Request Body:**
```json
{
    "customer_id": 1,
    "payment_method": "cash",
    "status": "paid",
    "items": [
        {
            "variant_id": 1,
            "quantity": 2
        },
        {
            "variant_id": 3,
            "quantity": 1
        }
    ]
}
```

**Response:**
```json
{
    "success": true,
    "message": "Bill created successfully",
    "data": {
        "bill": {
            "id": 2,
            "bill_number": "BILL-20240101-0002",
            "customer": {
                "id": 1,
                "name": "John Doe",
                "phone": "+1234567890"
            },
            "subtotal": 89.97,
            "total_amount": 89.97,
            "status": "paid",
            "payment_method": "cash",
            "created_at": "2024-01-01T12:00:00Z"
        }
    }
}
```

### GET /api/bills/{id}/
Get detailed bill information.

**Response:**
```json
{
    "success": true,
    "data": {
        "bill": {
            "id": 1,
            "bill_number": "BILL-20240101-0001",
            "customer": {
                "id": 1,
                "name": "John Doe",
                "phone": "+1234567890",
                "email": "john@example.com",
                "address": "123 Main St, City, State"
            },
            "items": [
                {
                    "id": 1,
                    "product": {
                        "id": 1,
                        "name": "Cotton Summer Dress"
                    },
                    "variant": {
                        "id": 1,
                        "sku": "DRESS-001-S-BLUE",
                        "size": "S",
                        "color": "Blue"
                    },
                    "quantity": 2,
                    "unit_price": 26.99,
                    "total": 53.98
                }
            ],
            "subtotal": 59.99,
            "discount_amount": 0.0,
            "tax_amount": 0.0,
            "total_amount": 59.99,
            "status": "paid",
            "payment_method": "cash",
            "created_at": "2024-01-01T12:00:00Z",
            "updated_at": "2024-01-01T12:00:00Z"
        }
    }
}
```

## Dashboard API

### GET /api/dashboard/stats/
Get dashboard statistics.

**Query Parameters:**
- `start_date` (string): Filter by start date (YYYY-MM-DD)
- `end_date` (string): Filter by end date (YYYY-MM-DD)

**Response:**
```json
{
    "success": true,
    "data": {
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
                "name": "Cotton Summer Dress",
                "total_quantity": 12,
                "total_revenue": 359.88
            }
        ]
    }
}
```

## Search API

### GET /api/search/customers/
Search customers by phone or name.

**Query Parameters:**
- `q` (string): Search query

**Response:**
```json
{
    "success": true,
    "data": {
        "customers": [
            {
                "id": 1,
                "name": "John Doe",
                "phone": "+1234567890",
                "email": "john@example.com"
            }
        ]
    }
}
```

### GET /api/search/products/
Search products by name or SKU.

**Query Parameters:**
- `q` (string): Search query

**Response:**
```json
{
    "success": true,
    "data": {
        "products": [
            {
                "id": 1,
                "name": "Cotton Summer Dress",
                "slug": "cotton-summer-dress",
                "category": "dress",
                "brand": "Fashion Brand",
                "min_price": 26.99,
                "image": "http://example.com/media/products/dress1.jpg",
                "in_stock": true
            }
        ]
    }
}
```

## Health Check

### GET /api/health/
Check API health status.

**Response:**
```json
{
    "success": true,
    "message": "API is running",
    "timestamp": "2024-01-01T12:00:00Z",
    "version": "1.0.0"
}
```

## Error Responses

All endpoints return consistent error responses:

```json
{
    "success": false,
    "message": "Error description",
    "errors": {
        "field_name": ["Error details"]
    }
}
```

### Common HTTP Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `500` - Internal Server Error

## Rate Limiting

Currently, there are no rate limits implemented. Consider implementing rate limiting for production use.

## Pagination

Most list endpoints support pagination with the following parameters:
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20, max: 100)

## Mobile App Integration

### Flutter/Dart Example

```dart
// Login API call
Future<Map<String, dynamic>> login(String username, String password) async {
  final response = await http.post(
    Uri.parse('http://localhost:8000/api/auth/login/'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'username': username,
      'password': password,
    }),
  );
  
  return jsonDecode(response.body);
}

// Get products with JWT token
Future<Map<String, dynamic>> getProducts(String token) async {
  final response = await http.get(
    Uri.parse('http://localhost:8000/api/products/'),
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $token',
    },
  );
  
  return jsonDecode(response.body);
}
```

### React Native Example

```javascript
// Login API call
const login = async (username, password) => {
  const response = await fetch('http://localhost:8000/api/auth/login/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });
  
  return response.json();
};

// Get products with JWT token
const getProducts = async (token) => {
  const response = await fetch('http://localhost:8000/api/products/', {
    method: 'GET',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  });
  
  return response.json();
};
```

## Security Considerations

1. **HTTPS**: Always use HTTPS in production
2. **Token Storage**: Store JWT tokens securely on mobile devices
3. **Input Validation**: All inputs are validated on the server
4. **CORS**: CORS is configured for development domains
5. **CSRF**: CSRF protection is enabled for web requests

## Testing

Use tools like Postman, Insomnia, or curl to test the APIs:

```bash
# Health check
curl http://localhost:8000/api/health/

# Login
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'

# Get products (with token)
curl http://localhost:8000/api/products/ \
  -H "Authorization: Bearer your_access_token"
```

## Support

For API support and issues, contact the development team or create an issue in the project repository.
