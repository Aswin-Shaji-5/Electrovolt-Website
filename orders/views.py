from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib import messages
from .models import Cart, Order
from products.models import Product
import razorpay
from django.conf import settings
from django.http import HttpResponseBadRequest

# ✅ Buyer Only Decorator (Safe)
def buyer_only(view_func):
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'buyer':
            return HttpResponse("Only buyers allowed ❌")
        return view_func(request, *args, **kwargs)
    return wrapper


# ✅ Add to Cart
@login_required
@buyer_only
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    cart_item, created = Cart.objects.get_or_create(
        user=request.user,
        product=product
    )

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, "Item added to cart ✅")
    return redirect('cart')


# ✅ View Cart
@login_required
@buyer_only
def cart_view(request):
    items = Cart.objects.filter(user=request.user)
    total = sum(item.total_price() for item in items)

    return render(request, 'orders/cart.html', {
        'items': items,
        'total': total
    })


# ✅ Checkout
@login_required
@buyer_only
def checkout(request):
    items = Cart.objects.filter(user=request.user)
    total = sum(item.total_price() for item in items)

    if total == 0:
        messages.error(request, "Cart is empty ❌")
        return redirect('cart')

    if request.method == 'POST':
        address = request.POST.get('address')

        if not address:
            messages.error(request, "Address is required ❌")
            return redirect('checkout')

        # 🔥 Convert to paise
        amount = int(total * 100)

        # Create Razorpay order
        payment = client.order.create({
            "amount": amount,
            "currency": "INR",
            "payment_capture": 1
        })

        # Store data temporarily in session
        request.session['order_address'] = address
        request.session['razorpay_order_id'] = payment['id']

        return render(request, 'orders/payment.html', {
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'payment': payment,
            'amount': amount,
            'total': total
        })

    return render(request, 'orders/checkout.html', {'total': total})


# ✅ Remove from Cart (NEW)
@login_required
@buyer_only
def remove_from_cart(request, item_id):
    item = get_object_or_404(Cart, id=item_id, user=request.user)
    item.delete()

    messages.success(request, "Item removed ❌")
    return redirect('cart')

#order history
@login_required
@buyer_only
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    return render(request, 'orders/order_history.html', {
        'orders': orders
    })

#order tracking
@login_required
@buyer_only
def track_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    return render(request, 'orders/track_order.html', {
        'order': order
    })


#cancel order
@login_required
@buyer_only
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Prevent cancelling delivered or already cancelled orders
    if order.status in ['Delivered', 'Cancelled']:
        messages.error(request, "This order cannot be cancelled ❌")
        return redirect('order_history')

    order.status = 'Cancelled'
    order.save()

    messages.success(request, "Order cancelled successfully ✅")
    return redirect('order_history')

#Razor pay client creation
client = razorpay.Client(auth=(
    settings.RAZORPAY_KEY_ID,
    settings.RAZORPAY_KEY_SECRET
))

    
@login_required
@buyer_only
def payment_success(request):
    payment_id = request.GET.get('payment_id')
    order_id = request.GET.get('order_id')
    signature = request.GET.get('signature')

    #  Basic validation
    if not all([payment_id, order_id, signature]):
        return HttpResponseBadRequest("Invalid payment response ❌")

    params_dict = {
        'razorpay_order_id': order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature
    }

    try:
        #  Verify signature
        client.utility.verify_payment_signature(params_dict)

        #  Get session data
        address = request.session.get('order_address')
        items = Cart.objects.filter(user=request.user)

        if not address or not items.exists():
            return HttpResponseBadRequest("Session expired or cart empty ❌")

        total = sum(item.total_price() for item in items)

        #  Create order AFTER payment success
        order = Order.objects.create(
            user=request.user,
            address=address,
            total_amount=total,
            status="Paid",  # 🔥 FIXED
            razorpay_order_id=order_id,
            razorpay_payment_id=payment_id,
            razorpay_signature=signature
        )

        #  Clear cart
        items.delete()

        #  Clean session
        request.session.pop('order_address', None)
        request.session.pop('razorpay_order_id', None)

        messages.success(request, "Payment successful 🎉")
        return redirect('order_history')

    except razorpay.errors.SignatureVerificationError:
        return HttpResponseBadRequest("Payment verification failed ❌")

    except Exception as e:
        print(e)  # for debugging
        return HttpResponseBadRequest("Something went wrong ❌")



        