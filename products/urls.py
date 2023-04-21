from django.urls import path
from products.views import ProductView

urlpatterns = [
    path('/create', ProductView.as_view()),
]
