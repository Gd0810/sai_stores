from django.core.mail import EmailMultiAlternatives
from datetime import timedelta
from django.utils.timezone import now

def send_order_confirmation_email(user, address, cart_items, grand_total, payment_method, estimated_delivery):
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
            <td style="text-align: right;">₹{40:.2f}</td>
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

    email_body = f"""
    <p>Hi <strong>{user.username}</strong>,</p>
    <p>Thank you for shopping with <strong>Sai-Stores</strong>!</p>
    <p>Your order has been placed successfully. Below are the details of your order:</p>
    {order_table}
    <h3>Billing Address</h3>
    <p>
    {address.locality}, {address.city}, {address.state} - {address.zipcode} <br>
    <strong>Phone:</strong> {user.phone_number} <br>
    <strong>Email:</strong> {user.email}
    </p>
    <p><strong>Estimated Delivery Date:</strong> {estimated_delivery.strftime('%Y-%m-%d')}</p>
    <p>Thank you for choosing Sai-Stores. We hope to serve you again soon!</p>
    <p>Best regards,<br><strong>The Sai-Stores Team</strong></p>
    """

    email = EmailMultiAlternatives(
        'Order Confirmation from Sai-Stores.com',
        'Your order has been placed successfully.',  # Plain text fallback
        'no-reply@sai-stores.com',
        [user.email],
    )
    email.attach_alternative(email_body, "text/html")
    email.send()
