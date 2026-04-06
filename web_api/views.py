from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from shop.models import Product, ProductImage, ProductVariant
from django.utils import timezone
from datetime import timedelta
from django.db.models import Min, Max, Sum, Q
from decimal import Decimal
from .serializers import ProductListSerializer, ProductDetailSerializer


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 1
    page_size_query_param = 'page'
    max_page_size = 12


class HomeAPIView(generics.ListAPIView):
    """
    Public Home API for users to view featured products, new arrivals with pagination
    """
    permission_classes = [AllowAny]
    serializer_class = ProductListSerializer  # Use advanced serializer
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Get products based on the requested section"""
        section = self.request.GET.get('section', 'featured')
        
        if section == 'featured':
            return Product.objects.filter(
                Q(is_featured=True) & Q(is_active=True)
            ).select_related(
                'brand'
            ).prefetch_related(
                'variants',
                'variants__size',
                'variants__color',
                'images'
            ).order_by('-created_at')
        
        elif section == 'new_arrivals':
            # Get products created in the last 30 days
            thirty_days_ago = timezone.now() - timedelta(days=30)
            return Product.objects.filter(
                Q(created_at__gte=thirty_days_ago) & Q(is_active=True)
            ).select_related(
                'brand'
            ).prefetch_related(
                'variants',
                'variants__size',
                'variants__color',
                'images'
            ).order_by('-created_at')
        
        # Default to all active products
        return Product.objects.filter(
            is_active=True
        ).select_related(
            'brand'
        ).prefetch_related(
            'variants',
            'variants__size',
            'variants__color',
            'images'
        ).order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """
        GET method to return home page data with featured products and new arrivals
        """
        try:
            section = request.GET.get('section', 'home')
            page_size = int(request.GET.get('page_size', 1))
            
            # Validate page_size
            page_size = min(max(page_size, 1), 12)  # Max 12 items per page
            
            # Get the appropriate queryset
            if section == 'home':
                # For home page, get both featured and new arrivals
                featured_queryset = Product.objects.filter(
                    Q(is_featured=True) & Q(is_active=True)
                ).select_related(
                    'brand'
                ).prefetch_related(
                    'variants',
                    'variants__size',
                    'variants__color',
                    'images'
                ).order_by('-created_at')[:page_size]
                
                thirty_days_ago = timezone.now() - timedelta(days=30)
                new_arrivals_queryset = Product.objects.filter(
                    Q(created_at__gte=thirty_days_ago) & Q(is_active=True)
                ).select_related(
                    'brand'
                ).prefetch_related(
                    'variants',
                    'variants__size',
                    'variants__color',
                    'images'
                ).order_by('-created_at')[:page_size]
                
                # Serialize data with advanced serializer
                featured_serializer = self.get_serializer(featured_queryset, many=True)
                new_arrivals_serializer = self.get_serializer(new_arrivals_queryset, many=True)
                
                return Response({
                    'success': True,
                    'message': 'Home data retrieved successfully',
                    'data': {
                        'featured_products': {
                            'results': featured_serializer.data,
                            'count': len(featured_serializer.data),
                            'view_more_url': f'/api/home/?section=featured&page_size={page_size}'
                        },
                        'new_arrivals': {
                            'results': new_arrivals_serializer.data,
                            'count': len(new_arrivals_serializer.data),
                            'view_more_url': f'/api/home/?section=new_arrivals&page_size={page_size}'
                        }
                    },
                    'metadata': {
                        'page_size': page_size,
                        'timestamp': timezone.now().isoformat()
                    }
                }, status=status.HTTP_200_OK)
            
            else:
                # For specific sections (featured or new_arrivals), use simple manual pagination
                queryset = self.filter_queryset(self.get_queryset())
                
                # Manual pagination to avoid DRF complexity
                page = int(request.GET.get('page', 1))
                total = queryset.count()
                start = (page - 1) * page_size
                end = start + page_size
                paginated_queryset = queryset[start:end]
                
                # Serialize the paginated data
                serializer = self.get_serializer(paginated_queryset, many=True)
                
                # Calculate pagination URLs
                base_url = request.build_absolute_uri(request.path)
                next_page = None
                prev_page = None
                
                if page < ((total + page_size - 1) // page_size):
                    next_page = f"{base_url}?section={section}&page={page + 1}&page_size={page_size}"
                
                if page > 1:
                    prev_page = f"{base_url}?section={section}&page={page - 1}&page_size={page_size}"
                
                # Return paginated response with URLs
                return Response({
                    'success': True,
                    'message': f'{section.replace("_", " ").title()} retrieved successfully',
                    'data': {
                        'results': serializer.data,
                        'pagination': {
                            'current_page': page,
                            'total_pages': (total + page_size - 1) // page_size,
                            'total_items': total,
                            'items_per_page': page_size,
                            'has_next': page < ((total + page_size - 1) // page_size),
                            'has_prev': page > 1,
                            'next_page_url': next_page,
                            'prev_page_url': prev_page,
                        }
                    }
                })
                
        except ValueError as e:
            return Response({
                'success': False,
                'message': 'Invalid parameters',
                'error': str(e),
                'error_type': 'validation_error'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Internal server error',
                'error': str(e),
                'error_type': 'internal_error',
                'timestamp': timezone.now().isoformat()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


