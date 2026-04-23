from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Category
from .forms import ProductForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from functools import wraps
from django.db.models import Q


# ✅ Home (Search + Category + Price + Sorting)
def home(request):
    query = request.GET.get('q', '').strip()
    category_id = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    sort = request.GET.get('sort')

    products = Product.objects.all()

    # 🔥 SHOW ONLY SELLER'S PRODUCTS
    if request.user.is_authenticated:
        role = getattr(request.user.userprofile, 'role', None)
        if role == 'seller':
            products = products.filter(user=request.user)

    # 🔍 Search
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(category__name__icontains=query)
        )

    # 📂 Category
    if category_id and category_id.isdigit():
        products = products.filter(category_id=category_id)

    # 💰 Price
    if min_price and min_price.isdigit():
        products = products.filter(price__gte=min_price)

    if max_price and max_price.isdigit():
        products = products.filter(price__lte=max_price)

    # 🔄 Sorting
    if sort == 'low':
        products = products.order_by('price')
    elif sort == 'high':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')

    #  Categories
    categories = Category.objects.all()

    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'selected_category': category_id,
        'min_price': min_price,
        'max_price': max_price,
        'selected_sort': sort,
    }

    return render(request, 'products/home.html', context)


#  Seller Only Decorator
def seller_only(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        if not hasattr(request.user, 'userprofile') or request.user.userprofile.role != 'seller':
            messages.error(request, "Access Denied ❌ (Only sellers allowed)")
            return redirect('home')

        return view_func(request, *args, **kwargs)
    return wrapper


#  Add Product
@login_required
@seller_only
def add_product(request):
    form = ProductForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if form.is_valid():
            product = form.save(commit=False)
            product.user = request.user
            product.save()
            messages.success(request, "Product added successfully ✅")
            return redirect('home')
        else:
            messages.error(request, "Error adding product ❌")

    return render(request, 'products/add_product.html', {'form': form})


#  Cart Page
@login_required
def cart(request):
    return render(request, 'products/cart.html')


# 🛒 Add to Cart
@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    messages.success(request, f"{product.name} added to cart 🛒")
    return redirect('home')


# ✅ Edit Product
@login_required
@seller_only
def edit_product(request, id):
    product = get_object_or_404(Product, id=id)

    # if hasattr(product, 'user') and product.user != request.user:
    #     messages.error(request, "You cannot edit this product ❌")
    #     return redirect('home')

    form = ProductForm(request.POST or None, request.FILES or None, instance=product)

    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Product updated successfully ✏️")
            return redirect('home')

    return render(request, 'products/add_product.html', {'form': form})


# ✅ Delete Product
@login_required
@seller_only
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)

    # if hasattr(product, 'user') and product.user != request.user:
    #     messages.error(request, "You cannot delete this product ❌")
    #     return redirect('home')

    product.delete()
    messages.success(request, "Product deleted successfully 🗑️")
    return redirect('home')