from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BusinessProfileViewSet, InvoiceViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'business-profiles', BusinessProfileViewSet, basename='businessprofile')
router.register(r'invoices', InvoiceViewSet, basename='invoice')

app_name = 'invoices'

urlpatterns = [
    path('', include(router.urls)),
]
