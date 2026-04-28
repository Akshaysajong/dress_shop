from django import forms
from django.forms import formset_factory
from .models import Product, ProductVariant, Brand, Size, Color, Material, StockAdjustment

class BrandForm(forms.ModelForm):
    class Meta:
        model = Brand
        fields = ['name', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3})
        }

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'brand', 'sku',
                  'category', 'gender',
                  'materials',
                  'base_price', 'selling_price', 'discount_percentage',
                  'main_image', 
                  'is_active', 'is_featured']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'base_price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'selling_price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'discount_percentage': forms.NumberInput(attrs={'step': '0.1', 'min': '0', 'max': '100'}),
        }

class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['size', 'color', 'quantity', 'price_override', 'image', 'sku']
        widgets = {
            'quantity': forms.NumberInput(attrs={'min': '0'}),
            'price_override': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

ProductVariantFormSet = formset_factory(ProductVariantForm, extra=3, can_delete=True)

class StockAdjustmentForm(forms.ModelForm):
    class Meta:
        model = StockAdjustment
        fields = ['adjustment_type', 'quantity_before', 'quantity_after', 'quantity_changed', 'reason']
        widgets = {
            'quantity_before': forms.NumberInput(attrs={'min': '0', 'class': 'form-control'}),
            'quantity_after': forms.NumberInput(attrs={'min': '0', 'class': 'form-control'}),
            'quantity_changed': forms.NumberInput(attrs={'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }

class QuickStockForm(forms.Form):
    quantity = forms.IntegerField(
        min_value=1,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter quantity'
        })
    )
    reason = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Reason (optional)'
        })
    )

class BulkStockForm(forms.Form):
    action = forms.ChoiceField(
        choices=[
            ('add', 'Add Stock'),
            ('reduce', 'Reduce Stock'),
            ('set', 'Set Stock Level')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    quantity = forms.IntegerField(
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter quantity'
        })
    )
    reason = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Reason (optional)'
        })
    )

class ProductFilterForm(forms.Form):
    search = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder': 'Search products...'
    }))
    category = forms.ChoiceField(choices=[('', 'All Categories')] + Product.CATEGORY_CHOICES, required=False)
    gender = forms.ChoiceField(choices=[('', 'All Genders')] + Product.GENDER_CHOICES, required=False)
    brand = forms.ModelChoiceField(queryset=Brand.objects.all(), required=False, empty_label="All Brands")
    size = forms.ModelChoiceField(queryset=Size.objects.all(), required=False, empty_label="All Sizes")
    color = forms.ModelChoiceField(queryset=Color.objects.all(), required=False, empty_label="All Colors")
    min_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0'}))
    max_price = forms.DecimalField(required=False, widget=forms.NumberInput(attrs={'step': '0.01', 'min': '0'}))
    is_active = forms.BooleanField(required=False, label='Active Only')
    is_featured = forms.BooleanField(required=False, label='Featured Only')
    stock_status = forms.ChoiceField(
        choices=[
            ('', 'All Stock Levels'),
            ('out', 'Out of Stock'),
            ('low', 'Low Stock'),
            ('limited', 'Limited Stock'),
            ('good', 'Good Stock')
        ],
        required=False
    )
