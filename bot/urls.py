from django.urls import path
from .views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('admins',AdminViewSet,basename='admins')
router.register('category',CategoryViewSet,basename='category')
router.register('product',ProductViewSet,basename='product')
router.register('order',OrderViewSet,basename='order')
router.register('question',QuestionViewSet,basename='question')
router.register('cart',CartViewSet,basename='cart')


urlpatterns = [
    
]+router.urls