from django.contrib import admin
from .models import *
from import_export.admin import ExportActionMixin


# Register your models here.


@admin.register(BotAdmin)
class BotAdminAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ['title', 'user_id', 'created_at', 'updated_at']
    list_filter = ['title', 'user_id', 'created_at', 'updated_at']
    search_fields = ['title', 'user_id', 'created_at', 'updated_at']
    list_per_page = 10
    readonly_fields = ['status', ]


@admin.register(Category)
class CategoryAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ['title', 'created_at', 'updated_at']
    list_filter = ['title', 'created_at', 'updated_at']
    search_fields = ['title', 'created_at', 'updated_at']
    list_per_page = 10


@admin.register(Product)
class ProductAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ['title', 'description', 'price', 'category', 'image', 'created_at', 'updated_at']
    list_filter = ['title', 'description', 'price', 'category', 'image', 'created_at', 'updated_at']
    search_fields = ['title', 'description', 'price', 'category', 'image', 'created_at', 'updated_at']
    list_per_page = 10


@admin.register(Order)
class OrderAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ['user_id', 'total_price', 'is_paid', 'is_finished', 'name', 'adress', 'created_at', 'updated_at']
    list_filter = ['user_id', 'total_price', 'is_paid', 'is_finished', 'name', 'adress', 'created_at', 'updated_at']
    search_fields = ['user_id', 'total_price', 'is_paid', 'is_finished', 'name', 'adress', 'created_at', 'updated_at']
    list_per_page = 10


@admin.register(Question)
class QuestionAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ['user_id', 'question', 'message_id', 'answer', 'is_answered', 'created_at', 'updated_at']
    list_filter = ['user_id', 'question', 'message_id', 'answer', 'is_answered', 'created_at', 'updated_at']
    search_fields = ['user_id', 'question', 'message_id', 'answer', 'is_answered', 'created_at', 'updated_at']
    list_per_page = 10


@admin.register(Cart)
class CartAdmin(ExportActionMixin, admin.ModelAdmin):
    list_display = ['product', 'user_id', 'quantity', 'created_at', 'updated_at']
    list_filter = ['product', 'user_id', 'quantity', 'created_at', 'updated_at']
    search_fields = ['product', 'user_id', 'quantity', 'created_at', 'updated_at']
    list_per_page = 10