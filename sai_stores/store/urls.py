from django.urls import path
from . import views
from .views import index


app_name = 'store'

urlpatterns = [
    path('', views.index, name='index'),
    # path('apple-products/', apple_products_view, name='apple-products'),
    path('category/<int:category_id>/', views.category_types, name='category_types'),
    path('type/<int:type_id>/', views.type_products, name='type_products'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/update/<int:cart_item_id>/', views.update_quantity, name='update_quantity'),
    path('cart/delete/<int:cart_item_id>/', views.delete_from_cart, name='delete_from_cart'),
    path('cart/', views.cart, name='cart'), 
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/', views.wishlist, name='wishlist'),  # Ensure this is present
    path('wishlist/toggle/<int:product_id>/', views.toggle_wishlist, name='toggle_wishlist'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('place_order/', views.place_order, name='place_order'),
    path('order_placed/', views.order_placed, name='order_placed'),
    path('search/', views.search, name='search'), 
    path('profile/', views.profile, name='profile'),
    path('address/', views.address_list, name='address_list'),
    path('address/add/', views.add_address, name='add_address'),
    path('address/update/<int:pk>/', views.update_address, name='update_address'), 
    path('address/delete/<int:pk>/', views.delete_address, name='delete_address'),
    path('update-profile-photo/', views.update_profile_photo, name='update_profile_photo'),
    path('orders/', views.orders_list, name='orders'),
    path('order/<int:order_id>/', views.order_details, name='order_details'),
    path('feedback/<int:product_id>/', views.submit_feedback, name='submit_feedback'),
    path("order/<int:order_id>/cancel/", views.confirm_order_cancel, name="confirm_order_cancel"),
    # path('verify-payment/', views.verify_razorpay_payment, name='verify_payment'),
    path('verify-razorpay-payment/', views.verify_razorpay_payment, name='verify_razorpay_payment'),  # ✅ Add this
    # path('order_confirmation/', views.order_confirmation, name='order_confirmation'),
    # path('test/', views.test, name='test'),
   
#    path('related-products/<int:product_id>/', views.related_products, name='related_products'),


    
   
    
   
]
