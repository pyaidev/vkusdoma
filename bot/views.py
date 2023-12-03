from django.shortcuts import render
from rest_framework.generics import ListAPIView, ListCreateAPIView
from .models import *
from .serializers import *
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action


class AdminViewSet(ModelViewSet):
    queryset = BotAdmin.objects.all()
    serializer_class = AdminSerializer

    def create(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        status_ = request.data.get('status')
        if admin := BotAdmin.objects.filter(user_id=user_id):
            admin = admin.first()
            admin.status = status_
            admin.save()
        return Response(status=status.HTTP_200_OK)
    
    @action(methods=['get',],detail=False)
    def get_admin(self, request):
        qs = self.queryset.filter(status=True)
        sz = self.serializer_class(qs,many=True)
        return Response(sz.data)



class CategoryViewSet(ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        cats = self.request.GET.get('cats', None)
        if cats:
            return self.queryset.filter(category=int(cats))
        return self.queryset.all()


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.filter(is_finished=False)
    serializer_class = OrderSerializer

    

    def create(self, request, *args, **kwargs):
        user_id = request.data.get('user_id')
        name = request.data.get('name')
        adress = request.data.get('adress')
        carts = Cart.objects.filter(user_id=user_id,is_deleted=False)
        total_price = 0
        for cart in carts:
            total_price += cart.product.price * cart.quantity
        order = Order.objects.create(
            user_id=user_id, name=name, adress=adress, total_price=total_price)
        order.carts.set(carts)
        carts.update(is_deleted=True)

        return Response(order.id,status=status.HTTP_200_OK)
    
    @action(methods=['get'],detail=True)
    def get_order(self, request, pk=None):
        qs = Order.objects.filter(user_id=pk)
        sz = OrderSerializer(qs,many=True)
        return Response(sz.data)

class QuestionViewSet(ModelViewSet):
    queryset = Question.objects.all().filter(is_answered=False)
    serializer_class = QuestionSerizliaer


class CartViewSet(ModelViewSet):
    queryset = Cart.objects.filter(is_deleted=False)
    serializer_class = CartSerializer

    def get_queryset(self):
        user_id = self.request.GET.get('user_id', None)
        if user_id:
            return self.queryset.filter(user_id=int(user_id))
        return self.queryset.all()

    def create(self, request, *args, **kwargs):
        product_id = request.data.get('product')
        user_id = request.data.get('user_id')
        quantity = request.data.get('quantity')
        product = Product.objects.get(id=product_id)
        cart = Cart.objects.filter(product=product, user_id=user_id,is_deleted=False)
        if cart:
            cart = cart.first()
            cart.quantity += int(quantity)
            cart.save()
        else:
            cart = Cart.objects.create(
                product=product, user_id=user_id, quantity=quantity)
        return Response(status=status.HTTP_200_OK)

    @action(methods=['delete'], detail=True)
    def delete_cart(self, request, pk=None):
        cart = Cart.objects.filter(user_id=pk)
        cart.delete()
        return Response(status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True)
    def carts(self, request, pk=None):
        cart = Cart.objects.filter(
            user_id=pk).values_list('product', flat=True)
        return Response({'cats': cart}, status=status.HTTP_200_OK)
