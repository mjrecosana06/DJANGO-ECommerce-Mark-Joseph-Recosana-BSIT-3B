from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
import json
import datetime
from .models import * 
from .utils import cookieCart, cartData, guestOrder
from django.contrib.auth.decorators import login_required

def store(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	products = Product.objects.all()
	context = {'products':products, 'cartItems':cartItems}
	return render(request, 'store/store.html', context)


def cart(request):
	data = cartData(request)

	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/cart.html', context)

def checkout(request):
	data = cartData(request)
	
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context = {'items':items, 'order':order, 'cartItems':cartItems}
	return render(request, 'store/checkout.html', context)

def updateItem(request):
	data = json.loads(request.body)
	productId = data['productId']
	action = data['action']
	print('Action:', action)
	print('Product:', productId)

	customer = request.user.customer
	product = Product.objects.get(id=productId)
	order, created = Order.objects.get_or_create(customer=customer, complete=False)

	orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

	if action == 'add':
		orderItem.quantity = (orderItem.quantity + 1)
	elif action == 'remove':
		orderItem.quantity = (orderItem.quantity - 1)

	orderItem.save()

	if orderItem.quantity <= 0:
		orderItem.delete()

	return JsonResponse('Item was added', safe=False)

def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    order.transaction_id = str(transaction_id)

    # For COD, we assume the total from the form is trusted
    if total == float(order.get_cart_total):
        order.complete = True
        order.payment_method = 'COD'
        order.save()

    if order.shipping:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
        )

    return JsonResponse('Order placed successfully with Cash on Delivery.', safe=False)

def registerPage(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords don't match!")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password1, first_name=first_name, last_name=last_name)
        Customer.objects.create(user=user, name=username, email=email)
        
        messages.success(request, "Account created successfully! Please login.")
        return redirect('login')

    return render(request, 'store/register.html')

def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('store')
        else:
            messages.error(request, "Invalid username or password!")

    return render(request, 'store/login.html')

def logoutPage(request):
    logout(request)
    return redirect('store')

@login_required
def my_orders(request):
    orders = Order.objects.filter(customer=request.user.customer).order_by('-date_ordered')
    return render(request, 'store/my_orders.html', {'orders': orders})

def about(request):
    return render(request, 'store/about.html')

@login_required
def confirm_order_received(request, order_id):
    order = Order.objects.filter(id=order_id, customer=request.user.customer).first()
    if not order or order.status != 'shipped':
        return HttpResponseForbidden('You cannot confirm this order.')
    order.status = 'delivered'
    order.save()
    messages.success(request, 'Thank you for confirming receipt of your order!')
    return redirect('my_orders')

