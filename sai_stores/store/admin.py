from django.contrib import admin
from tinymce.widgets import TinyMCE
from django.db import models
from .models import (
    ProductCategory, ProductType, Product, Cart, Address, Order,
    Wishlist, Feedback, ProductMedia , OrderCancel
)

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

@admin.register(ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'actual_price', 'discounted_price')
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

admin.site.register(ProductMedia)

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'quantity')

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product')
    search_fields = ('user__username', 'product__name')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'city', 'state', 'zipcode')

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'product', 'status', 'order_date')
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'rating', 'comment')
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }
class OrderCancelAdmin(admin.ModelAdmin):
    list_display = ("order", "user", "reason", "canceled_at")
    search_fields = ("order__id", "user__username", "reason")
    list_filter = ("canceled_at",)

admin.site.register(OrderCancel, OrderCancelAdmin)