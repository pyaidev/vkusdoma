from rest_framework import serializers
from .models import *


class AdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = BotAdmin
        fields = ['user_id',]


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ['id', 'title', 'created_at', 'updated_at']


class ProductSerializer(serializers.ModelSerializer):
    category_title = serializers.CharField(
        source="category.title", read_only=True)
    image = serializers.URLField()

    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'category',
                  "category_title", 'image', 'created_at', 'updated_at']


class CartSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(
        source="product.title", read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'product', "product_title",
                  'user_id', 'quantity', 'created_at', 'updated_at']


class OrderSerializer(serializers.ModelSerializer):
    

    class Meta:
        model = Order
        fields = ['id', 
                  'user_id', 'name', 'total_price','adress', 'is_paid','is_finished']


class QuestionSerizliaer(serializers.ModelSerializer):
    question = serializers.CharField(required=False)
    user_id = serializers.CharField(required=False)
    message_id = serializers.CharField(required=False)

    class Meta:
        model = Question
        fields = "__all__"
