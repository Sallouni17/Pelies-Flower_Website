import datetime
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.contrib.auth.models import User
from flask import json
from .models import *
from .utils import cookieCart, cartData, guestOrder
import datetime

# Create your views here.
from django.http import HttpResponse, JsonResponse


def home(request):
    cartItems = cartData(request)['cartItems']
    context = {'cartItems':cartItems}
    return render(request, 'pelies/home.html', context)

def shop(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    products = Product.objects.all()
    context = {'products':products, 'cartItems':cartItems}
    return render(request, 'pelies/shop.html', context)

def cart(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'pelies/cart.html', context)

def checkout(request):
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']
    context = {'items':items, 'order':order, 'cartItems':cartItems}
    return render(request, 'pelies/checkout.html', context)

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
	order.transaction_id = transaction_id

	if total == order.get_cart_total:
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city=data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode'],
	    )
        

	return JsonResponse('Payment submitted..', safe=False)    

def get_in_touch(request):
    cartItems = cartData(request)['cartItems']
    context = {'cartItems':cartItems}
    return render(request, "pelies/contact.html", context)

def signup(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')

        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered.")
            return redirect('signup')

        user = User.objects.create_user(
            username=email,
            email=email,
            password=password1,
            first_name=first_name,
            last_name=last_name
        )
        user.save()
        login(request, user)
        messages.success(request, "Account created successfully!")
        return redirect(home)

    return render(request, 'pelies/signup.html')

def signin(request):
    if request.method == 'POST':
        username_or_email = request.POST.get('username')  # field name in your form
        password = request.POST.get('password')

        # Allow login by email or username
        user = None
        if '@' in username_or_email:
            try:
                # find the username linked to this email
                user_obj = User.objects.get(email=username_or_email)
                user = authenticate(request, username=user_obj.username, password=password)
            except User.DoesNotExist:
                user = None
        else:
            user = authenticate(request, username=username_or_email, password=password)

        # If authentication successful
        if user is not None:
            login(request, user)
            messages.success(request, "You have signed in successfully!")
            return redirect('shop')  # Redirect to the main shop page
        else:
            messages.error(request, "Invalid username/email or password.")

    return render(request, 'pelies/signin.html')

def logout_view(request):
    logout(request)
    messages.success(request, "You have logged out successfully!")
    return redirect('home')

def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']
    print('Action:', action)
    print('Product ID:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer)

    orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

    if action == 'add':
        orderItem.quantity += 1
    elif action == 'remove':
        orderItem.quantity -= 1

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()
    return JsonResponse("Item was added", safe=False)

def product_detail(request, pk):
    cartItems = cartData(request)['cartItems']
    context = {'cartItems':cartItems}
    product = get_object_or_404(Product, pk=pk)
    context['product'] = product
    return render(request, 'pelies/product_detail.html', context)

def our_story(request):
    cartItems = cartData(request)['cartItems']
    context = {'cartItems':cartItems}
    return render(request, 'pelies/our_story.html', context)
