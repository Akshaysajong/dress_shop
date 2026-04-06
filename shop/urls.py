from django.urls import path
from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('customers/', views.customer_management, name='customer_management'),
    path('customers/<int:customer_id>/edit/', views.edit_customer, name='edit_customer'),
    path('customers/<int:customer_id>/delete/', views.delete_customer, name='delete_customer'),
    path('customers/<int:customer_id>/', views.customer_detail, name='customer_detail'),
    path('products/', views.product_stock_management, name='product_stock_management'),
    path('products/add-brand/', views.add_brand, name='add_brand'),
    path('products/all/', views.product_list, name='product_list'),
    path('products/<slug:product_slug>/', views.product_detail, name='product_detail'),
    path('products/<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('products/add-stock/<int:variant_id>/', views.add_stock, name='add_stock'),
    path('products/reduce-stock/<int:variant_id>/', views.reduce_stock, name='reduce_stock'),
    path('quick-add-stock/', views.quick_add_stock, name='quick_add_stock'),
    path('bulk-stock-operation/', views.bulk_stock_operation, name='bulk_stock_operation'),
    path('stock-history/', views.stock_history, name='stock_history'),
    path('bills/', views.bill_list, name='bill_list'),
    path('bills/create/', views.create_bill, name='create_bill'),
    path('bills/<str:bill_number>/', views.bill_detail, name='bill_detail'),
    path('api/search-customer/', views.search_customer_by_phone, name='search_customer_by_phone'),
    path('api/variant-price/', views.get_variant_price, name='get_variant_price'),
    path('api/product-variants/', views.get_product_variants, name='get_product_variants'),
    path('sales/', views.sales_report, name='sales_report'),
    path('sales/data/', views.get_sales_data, name='get_sales_data'),
]
