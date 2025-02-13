from django.db import models
from accounts.models import CustomUser
from django.conf import settings
from django.contrib.auth.models import User
from tinymce.models import HTMLField
from django.utils.timezone import now
from django.utils.timezone import now
# from store.models import Product

class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='category_images/')

    def __str__(self):
        return self.name

class ProductType(models.Model):
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='types')
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='type_images/')

    def __str__(self):
        return f"{self.category.name} -> {self.name}"


class Product(models.Model):
    type = models.ForeignKey(ProductType, on_delete=models.CASCADE, null=True, blank=True)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=100)
    basic_description = HTMLField()
    description = HTMLField() 
    actual_price = models.FloatField()
    discounted_price = models.FloatField()
    image = models.ImageField(upload_to='product_images/')
    created_at = models.DateTimeField(auto_now_add=True) 

    def __str__(self):
        return self.name


class ProductMedia(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="media_files")
    file = models.FileField(upload_to='product_media/')

    def is_image(self):
        return self.file.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))

    def is_video(self):
        return self.file.name.lower().endswith(('.mp4', '.mov', '.avi', '.webm'))

    def __str__(self):
        return f"Media for {self.product.name} ({'Image' if self.is_image() else 'Video'})"



class Cart(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def total_price(self):
        return self.quantity * self.product.discounted_price
    
class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="wishlist")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="wishlisted_by")

    class Meta:
        unique_together = ('user', 'product')  # Prevent duplicate entries

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    locality = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zipcode = models.CharField(max_length=10)
    mobile = models.CharField(max_length=15)

    def __str__(self):
        return f"{self.name}, {self.locality}, {self.city}"

class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    # created_at = models.DateTimeField(auto_now_add=True)  
    status_choices = [
        ('Ordered', 'Ordered'),
        ('Shipped', 'Shipped'),
        ('Packed', 'Packed'),
        ('On the Way', 'On the Way'),
        ('Delivered', 'Delivered'),
        ('Canceled', 'Canceled'),
    ]
    status = models.CharField(max_length=20, choices=status_choices, default='Ordered')
    payment_method_choices = [
        ('COD', 'Cash on Delivery'),
        ('Online', 'Online Payment'),
    ]
    payment_method = models.CharField(max_length=20, choices=payment_method_choices, default='COD')
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class Feedback(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews")
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating} ⭐)"


   
class OrderCancel(models.Model):
    order = models.OneToOneField("Order", on_delete=models.CASCADE, related_name="cancellation")
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    reason = models.TextField()
    canceled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.order.id} Canceled by {self.user.username}"    