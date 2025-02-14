from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.timezone import now, timedelta
from django.core.paginator import Paginator
from django.core.mail import send_mail
from .forms import AddressForm, FeedbackForm
from django.http import HttpResponse
from django.http import JsonResponse
from django.core.mail import EmailMultiAlternatives
from django.utils.html import format_html
from accounts.models import CustomUser  # Import from accounts app
from accounts.forms import UserRegistrationForm  # Import the form
from django.contrib.auth.decorators import login_required
from .models import ProductCategory, ProductType, Product, Cart, Address, Order, Wishlist ,Feedback , Address, Order ,ProductMedia ,OrderCancel
import razorpay
from store.utils import send_order_confirmation_email
from django.conf import settings
# Home page

# def index(request):
#     categories = ProductCategory.objects.all()
#     return render(request, 'store/index.html', {'categories': categories})


from django.shortcuts import render

def custom_404(request, exception=None):
    return render(request, 'store/404.html', status=404)

def custom_404(request, exception=None):
    return render(request, "store/404.html", status=404)



def index(request):
    categories = ProductCategory.objects.all()
    
    # Debugging output
    print("Categories Count:", categories.count())
    for category in categories:
        print(f"ID: {category.id}, Name: {category.name}, Image: {category.image}")

    return render(request, 'store/index.html', {'categories': categories})

def category_context(request):
    return {'categories': ProductCategory.objects.all()}



# Display product types under a category
def category_types(request, category_id):
    category = get_object_or_404(ProductCategory, id=category_id)
    types = ProductType.objects.filter(category=category)
    return render(request, 'store/category_types.html', {'category': category, 'types': types})

# Display products under a product type
# def type_products(request, type_id):
#     product_type = get_object_or_404(ProductType, id=type_id)
#     products = Product.objects.filter(type=product_type)
#     return render(request, 'store/type_products.html', {'product_type': product_type, 'products': products})


def type_products(request, type_id):
    product_type = get_object_or_404(ProductType, id=type_id)
    products = Product.objects.filter(type=product_type)
    paginator = Paginator(products, 12)  # Show 12 products per page

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'store/type_products.html', {
        'product_type': product_type,
        'page_obj': page_obj
    })

# Display product details
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    media_files = ProductMedia.objects.filter(product=product)  # Fetch related media files

    can_review = False  # Default: user cannot review

    if request.user.is_authenticated:
        # Check if user has ordered this product and it's delivered
        can_review = Order.objects.filter(user=request.user, product=product, status="Delivered").exists()

    return render(request, 'store/product_detail.html', {
        'product': product,
        'media_files': media_files,  # Pass media files to template
        'can_review': can_review
    })
# Toggle wishlist
@login_required
def toggle_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    wishlist_item, created = Wishlist.objects.get_or_create(user=request.user, product=product)

    if created:
        messages.success(request, f"{product.name} has been added to your wishlist.")
    else:
        wishlist_item.delete()
        messages.success(request, f"{product.name} has been removed from your wishlist.")

    return redirect('store:wishlist')  # ✅ Redirects to the wishlist page





# Display wishlist
@login_required
def wishlist(request):
    wishlist_items = Wishlist.objects.filter(user=request.user)
    return render(request, 'store/wishlist.html', {'wishlist_items': wishlist_items})

# Add to cart
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    return redirect('store:cart')

# Delete item from cart
@login_required
def delete_from_cart(request, cart_item_id):
    if request.method == "POST":
        cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
        cart_item.delete()
    return redirect('store:cart')



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
@login_required
@csrf_exempt
def update_quantity(request, cart_item_id):
    if request.method == "POST":
        cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
        data = json.loads(request.body)
        quantity = data.get('quantity', cart_item.quantity)

        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            item_total = cart_item.product.discounted_price * cart_item.quantity
            cart_total = sum(
                item.product.discounted_price * item.quantity for item in Cart.objects.filter(user=request.user)
            ) + 40  # Add shipping fee

            return JsonResponse({'item_total': f"{item_total}", 'cart_total': f"{cart_total}"})

    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    addresses = Address.objects.filter(user=request.user)
    total_price = sum(item.product.discounted_price * item.quantity for item in cart_items) + 40  # Add shipping fee

    if request.method == "POST":
        address_id = request.POST.get("address")
        payment_method = request.POST.get("payment_method")

        if not address_id:
            messages.error(request, "Please select a valid address.")
            return redirect("store:cart")

        address = get_object_or_404(Address, id=address_id, user=request.user)
        if not cart_items.exists():
            messages.error(request, "Your cart is empty!")
            return redirect("store:cart")

        estimated_delivery = now() + timedelta(days=5)
        shipping_fee = 40
        total_price = sum([item.product.discounted_price * item.quantity for item in cart_items])
        grand_total = total_price + shipping_fee

        # Create orders for each product
        for cart_item in cart_items:
            Order.objects.create(
                user=request.user,
                product=cart_item.product,
                address=address,
                quantity=cart_item.quantity,
                status="Ordered",
                payment_method=payment_method
            )

        # Clear the cart
        cart_items.delete()

        messages.success(request, "Order placed successfully!")
        return redirect("store:profile")

    return render(request, "store/cart.html", {"cart_items": cart_items, "addresses": addresses, "total_price": total_price})


# Place order
@login_required
def place_order(request):
    if request.method == 'POST':
        address_id = request.POST.get('address')
        payment_method = request.POST.get('payment_method')

        # Validate address selection
        if not address_id:
            messages.error(request, "Please select a valid address.")
            return redirect('store:place_order')

        address = get_object_or_404(Address, id=address_id, user=request.user)
        cart_items = Cart.objects.filter(user=request.user)
        if not cart_items.exists():
            messages.error(request, "Your cart is empty!")
            return redirect('store:cart')

        estimated_delivery = now() + timedelta(days=5)
        shipping_fee = 40  # Fixed shipping charge
        total_price = sum([item.product.discounted_price * item.quantity for item in cart_items])
        grand_total = total_price + shipping_fee  # Adding shipping fee to total

        # Create order table
        order_table = """
        <table border="1" cellspacing="0" cellpadding="8" style="border-collapse: collapse; width: 100%;">
            <tr>
                <th style="background-color: #f2f2f2; text-align: left;">Product</th>
                <th style="background-color: #f2f2f2; text-align: center;">Quantity</th>
                <th style="background-color: #f2f2f2; text-align: right;">Price</th>
            </tr>
        """
        for item in cart_items:
            order_table += f"""
            <tr>
                <td>{item.product.name}</td>
                <td style="text-align: center;">{item.quantity}</td>
                <td style="text-align: right;">₹{item.product.discounted_price * item.quantity:.2f}</td>
            </tr>
            """
        order_table += f"""
            <tr>
                <td colspan="2" style="text-align: right; font-weight: bold;">Shipping Fee:</td>
                <td style="text-align: right;">₹{shipping_fee:.2f}</td>
            </tr>
            <tr>
                <td colspan="2" style="text-align: right; font-weight: bold;">Payment Method:</td>
                <td style="text-align: right;">{payment_method}</td>
            </tr>
            <tr>
                <td colspan="2" style="text-align: right; font-weight: bold;">Total:</td>
                <td style="text-align: right;">₹{grand_total:.2f}</td>
            </tr>
        </table>
        """

        # Create orders
        for item in cart_items:
            Order.objects.create(
                user=request.user,
                product=item.product,
                address=address,
                quantity=item.quantity,
                payment_method=payment_method,
                order_date=now(),
                status='Ordered',
            )

        # Clear cart
        cart_items.delete()

        # Send confirmation email
        email_body = f"""
        <p>Hi <strong>{request.user.username}</strong>,</p>
        <p>Thank you for shopping with <strong>Sai-Stores</strong>!</p>
        <p>Your order has been placed successfully. Below are the details of your order:</p>

        {order_table}

        <h3>Billing Address</h3>
        <p>
        {address.locality}, {address.city}, {address.state} - {address.zipcode} <br>
        <strong>Phone:</strong> {request.user.phone_number} <br>
        <strong>Email:</strong> {request.user.email}
        </p>

        <p><strong>Estimated Delivery Date:</strong> {estimated_delivery.strftime('%Y-%m-%d')}</p>
        <p>Thank you for choosing Sai-Stores. We hope to serve you again soon!</p>

        <p>Best regards,<br><strong>The Sai-Stores Team</strong></p>
        """

        email = EmailMultiAlternatives(
            'Order Confirmation from Sai-Stores.com',
            'Your order has been placed successfully.',  # Plain text fallback
            'no-reply@sai-stores.com',
            [request.user.email],
        )
        email.attach_alternative(email_body, "text/html")
        email.send()

        messages.success(request, 'Order placed successfully!')
        return redirect('store:order_placed')

    addresses = Address.objects.filter(user=request.user)
    return render(request, 'store/cart.html', {'addresses': addresses})


@login_required
def order_placed(request):
    recent_orders = Order.objects.filter(user=request.user).order_by('-order_date')[:5]
    
    if recent_orders:
        order_date = recent_orders[0].order_date
        delivery_date = order_date + timedelta(days=5)
    else:
        order_date = None
        delivery_date = None

    context = {
        'recent_orders': recent_orders,
        'order_date': order_date.strftime('%d %b %Y') if order_date else '',
        'delivery_date': delivery_date.strftime('%d %b %Y') if delivery_date else '',
    }
    return render(request, 'store/order_placed.html', context)



from django.shortcuts import render
from .models import Product


from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Product, ProductCategory, ProductType

@login_required
def search(request):
    query = request.GET.get('search', '')
    category_filter = request.GET.get('category', '')
    type_filter = request.GET.get('type', '')
    price_filter = request.GET.get('price', '')

    # Base queryset
    products = Product.objects.all()

    # Filter by search query (name or description)
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))

    # Filter by category
    if category_filter:
        products = products.filter(category_id=category_filter)

    # Filter by product type
    if type_filter:
        # Ensure the selected type belongs to the selected category (if category is selected)
        if category_filter:
            products = products.filter(type_id=type_filter, type__category_id=category_filter)
        else:
            products = products.filter(type_id=type_filter)

    # Filter by price range
    if price_filter:
        min_price, max_price = map(float, price_filter.split('-'))
        products = products.filter(discounted_price__gte=min_price, discounted_price__lte=max_price)

    # Get all available filters for the dropdowns
    categories = ProductCategory.objects.all()
    types = ProductType.objects.filter(category_id=category_filter) if category_filter else ProductType.objects.all()

    return render(request, 'store/search.html', {
        'products': products,
        'categories': categories,
        'types': types,
    })

@login_required

def address_list(request):
    addresses = Address.objects.filter(user=request.user)
    form = AddressForm()
    return render(request, 'store/profile.html', {'addresses': addresses, 'form': form})

def add_address(request):
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user  # Automatically assign logged-in user
            address.save()
            return redirect('store:profile')
    else:
        form = AddressForm()

    return render(request, 'store/add_address.html', {'form': form})


def update_address(request, pk):
    address = get_object_or_404(Address, pk=pk)

    # Prevent unauthorized users from updating others' addresses
    if request.user != address.user:
        return redirect('store:profile')

    if request.method == "POST":
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('store:profile')
    else:
        form = AddressForm(instance=address)

    return render(request, 'store/update_address.html', {'form': form})




def delete_address(request, pk):
    address = get_object_or_404(Address, pk=pk)
    
    if request.method == "POST":
        address.delete()
        return redirect('store:profile')  # Redirect to address list after deletion

    return render(request, 'store/confirm_delete.html', {'address': address})


def update_profile_photo(request):
    if request.method == "POST" and request.FILES.get("photo"):
        user = request.user
        user.photo = request.FILES["photo"]  # Update the photo field
        user.save()  # Save the updated user instance
        return JsonResponse({"success": True, "photo_url": user.photo.url})

    return JsonResponse({"success": False, "error": "Invalid request"})






def orders_list(request):
    # Get all orders for the logged-in user, ordered by order_date (newest first)
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    
    
    # Paginate the orders - 10 orders per page
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_orders = paginator.get_page(page_number)

    return render(request, 'store/orders.html', {'orders': page_orders})
  



@login_required
def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'store/order_details.html', {'order': order})



@login_required
def submit_feedback(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == "POST":
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')

        Feedback.objects.create(
            user=request.user,
            product=product,
            rating=rating,
            comment=comment
        )

        return redirect('store:product_detail', product_id=product.id)

    return redirect('store:profile')


@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).select_related('product__type', 'product__category').order_by('-order_date')

    total_orders = orders.count()
    total_complete_orders = orders.filter(status="Delivered").count()
    wishlist_count = Wishlist.objects.filter(user=request.user).count()
    wishlist_items = Wishlist.objects.filter(user=request.user)
    addresses = Address.objects.filter(user=request.user)

    return render(request, 'store/profile.html', {
        'orders': orders[:25],  # Show latest 5 orders
        'total_orders': total_orders,
        'total_complete_orders': total_complete_orders,
        'wishlist_count': wishlist_count,
        'addresses': addresses,
        'wishlist_items': wishlist_items
    })


















def index(request):
    top_products = Product.objects.order_by('-actual_price')[:10]
    return render(request, 'store/index.html', {'top_products': top_products})

def index(request):
    top_products = Product.objects.order_by('-actual_price')[:10]
    apple_types = ProductType.objects.filter(name__icontains='Apple')
    apple_products = Product.objects.filter(type__in=apple_types)
    return render(request, 'store/index.html', {'top_products': top_products, 'apple_products': apple_products})


from django.shortcuts import render
from .models import Product, ProductType

from django.shortcuts import render
from .models import Product, ProductType

def index(request):
    top_products = Product.objects.order_by('-actual_price')[:10]
    apple_types = ProductType.objects.filter(name__icontains='Apple')
    apple_products = Product.objects.filter(type__in=apple_types)
    
    # Exclude products with empty image fields
    recent_products = Product.objects.exclude(image="").exclude(image__isnull=True).order_by('-created_at')[:9]
    
    return render(request, 'store/index.html', {
        'top_products': top_products,
        'apple_products': apple_products,
        'recent_products': recent_products
    })


def product_detail(request, product_id):
    # Get the current product
    product = get_object_or_404(Product, id=product_id)

    # Get related products (same category, exclude the current product)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id)[:10]
    
    # Calculate the total count of ratings
    total_ratings = Feedback.objects.filter(product=product).count()

    return render(request, 'store/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'total_ratings': total_ratings,
    })

def confirm_order_cancel(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    if request.method == "POST":
        if "confirm" in request.POST:
            cancel_reason = request.POST.get("cancel_reason", "").strip()  # Ensure non-empty input

            if not cancel_reason:
                messages.error(request, "Please provide a cancellation reason.")
                return render(request, "store/confirm_order_cancel.html", {"order": order})

            # Create a cancellation entry
            OrderCancel.objects.create(order=order, user=request.user, reason=cancel_reason)

            # Update the order status to "Canceled"
            order.status = "Canceled"
            order.save()

            messages.success(request, "Your order has been canceled successfully.")
            return redirect("store:profile")

    return render(request, "store/confirm_order_cancel.html", {"order": order})
   
   
   
   
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


def place_order(request):
    if request.method == 'POST':
        address_id = request.POST.get('address')
        payment_method = request.POST.get('payment_method')

        if not address_id:
            messages.error(request, "Please select a valid address.")
            return redirect('store:place_order')

        address = get_object_or_404(Address, id=address_id, user=request.user)
        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items.exists():
            messages.error(request, "Your cart is empty!")
            return redirect('store:cart')

        estimated_delivery = now() + timedelta(days=5)
        shipping_fee = 40
        total_price = sum([item.product.discounted_price * item.quantity for item in cart_items])
        grand_total = total_price + shipping_fee

        # Handling COD orders
        if payment_method == "COD":
            order_items = []
            for item in cart_items:
                order = Order.objects.create(
                    user=request.user,
                    product=item.product,
                    address=address,
                    quantity=item.quantity,
                    payment_method=payment_method,
                    order_date=now(),
                    status='Ordered',
                )
                order_items.append(order)

            cart_items.delete()
            send_order_confirmation_email(request.user, address, order_items, grand_total, payment_method, estimated_delivery)  # Using utils.py function
            messages.success(request, 'Order placed successfully!')
            return redirect('store:order_placed')

        # Handling Razorpay orders
        elif payment_method == "Razorpay":
            razorpay_order = razorpay_client.order.create({
                "amount": int(grand_total * 100),  # Convert to paise
                "currency": "INR",
                "payment_capture": "1"
            })

            return JsonResponse({
                "order_id": razorpay_order["id"],
                "amount": grand_total,
                "currency": "INR",
                "key": settings.RAZORPAY_KEY_ID
            })

    return redirect('store:cart')


def verify_razorpay_payment(request):
    if request.method == "POST":
        razorpay_payment_id = request.POST.get("razorpay_payment_id")
        razorpay_order_id = request.POST.get("razorpay_order_id")
        razorpay_signature = request.POST.get("razorpay_signature")

        params_dict = {
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature
        }

        try:
            # Verify Razorpay payment
            razorpay_client.utility.verify_payment_signature(params_dict)

            # Create order in the database
            user = request.user
            cart_items = Cart.objects.filter(user=user)
            if not cart_items.exists():
                messages.error(request, "Your cart is empty! Payment verification failed.")
                return redirect('store:cart')

            address = Address.objects.filter(user=user).first()
            estimated_delivery = now() + timedelta(days=5)
            shipping_fee = 40
            total_price = sum([item.product.discounted_price * item.quantity for item in cart_items])
            grand_total = total_price + shipping_fee

            order_items = []
            for item in cart_items:
                order = Order.objects.create(
                    user=user,
                    product=item.product,
                    address=address,
                    quantity=item.quantity,
                    payment_method="Razorpay",
                    payment_id=razorpay_payment_id,
                    order_date=now(),
                    status='Ordered',
                )
                order_items.append(order)

            cart_items.delete()

            # Send confirmation email using utils.py function
            send_order_confirmation_email(user, address, order_items, grand_total, "Razorpay", estimated_delivery)

            messages.success(request, "Payment successful! Order placed.")
            return redirect('store:order_placed')

        except razorpay.errors.SignatureVerificationError:
            messages.error(request, "Payment verification failed!")
            return redirect('store:cart')

    return redirect('store:cart')
