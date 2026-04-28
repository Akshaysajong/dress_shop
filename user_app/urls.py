from django.urls import path
from . import views

app_name = 'shop_public'

urlpatterns = [
    path('home/', views.home, name='home'),
    path('products/', views.products_list, name='shop_public_products_list'),
    path('product/<slug:slug>/', views.product_detail, name='shop_public_product_detail'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('login/', views.login, name='login'),
]
