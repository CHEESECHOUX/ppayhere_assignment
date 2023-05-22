from django.urls import path
from products.views import ProductCreateView, ProductListView, ProductDetailView, ProductSearchView, ProductChosungView, ProductUpdateView, ProductDeleteView

urlpatterns = [
    path('/create', ProductCreateView.as_view(), name='product-create'),
    path('/list', ProductListView.as_view(), name='product-list'),
    path('/detail/<str:category>/<int:pk>',
         ProductDetailView.as_view(), name='product-detail'),
    path('/search/', ProductSearchView.as_view(), name='product-search'),
    path('/update/<int:pk>', ProductUpdateView.as_view(), name='product-update'),
    path('/delete/<int:pk>', ProductDeleteView.as_view(), name='product-delete'),
]
