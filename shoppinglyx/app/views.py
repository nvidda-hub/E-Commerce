import re
from django.http.response import JsonResponse
from django.shortcuts import render, redirect 
from django.utils.translation import activate
from django.views import View
import pymongo
from app.forms import CustomerRegistrationForm, MyPasswordResetForm, CustomerProfileForm
from app.models import Product, Customer, OrderPlaced, Cart
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required       # for function based view
from django.utils.decorators import method_decorator            # for class based view putting login_required


# for email
from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.conf import settings
from django.core.cache.backends.base import DEFAULT_TIMEOUT
from django.views.decorators.cache import cache_page


db_client = pymongo.MongoClient('mongodb://localhost:27017/')
db = db_client.shop_database


CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)


# def home(request):                # Function Based view
#  return render(request, 'app/home.html')

class HomeView(View):               # class based view
    def get(self, request):
        laptops = db.app_product.find({"category":"L"})
        mobiles = db.app_product.find({"category":"M"})
        bottomwears = db.app_product.find({"category":"BW"})
        topwears = db.app_product.find({"category":"TW"})
        return render(request, 'app/home.html', {"laptops":laptops, "mobiles":mobiles, "bottomwears":bottomwears, "topwears":topwears})
        

# def product_detail(request):
#  return render(request, 'app/productdetail.html')

class ProductDetailView(View):
    def get(self, request, pk):
        product = db.app_product.find_one({"id":pk})
        item_already_in_cart = False
        if request.user.is_authenticated:
            item_already_in_cart = Cart.objects.filter(Q(product=pk) & Q(user=request.user)).exists()
        return render(request, 'app/productdetail.html', {"product":product, 'item_already_in_cart':item_already_in_cart})

@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = Product.objects.get(id=product_id)
    data_for_cart = Cart(user=user, product=product)
    data_for_cart.save()
    return redirect('/show-cart')

@login_required
def show_cart(request):
    if request.user.is_authenticated:
        user = request.user
        cart = Cart.objects.filter(user=user)
        amount = 0.0
        shipping_amount = 70.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == user]
        if cart_product:
            for p in cart_product:
                amount = amount + (p.quantity * p.product.discounted_price)
        total_amount = amount + shipping_amount
        return render(request, 'app/addtocart.html', {'carts':cart, 'total_amount':total_amount, 'amount':amount})

# using AJAX to avoid page from refreshing
def plus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user)) # get to fetch one object
        c.quantity = c.quantity + 1
        c.save()
        amount = 0.0
        shipping_amount = 70.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        if cart_product:
            for p in cart_product:
                amount = amount + (p.quantity * p.product.discounted_price)
        total_amount = amount + shipping_amount
        
        data = {
            'quantity':c.quantity,
            'amount':amount,
            'totalamount':total_amount
        }
        return JsonResponse(data)   # this data goes to respective javascript file


def minus_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        if c.quantity > 0:
            c.quantity -= 1
            c.save()
            amount = 0.0
            shipping_amount = 70.0
            total_amount = 0.0
            cart_product = [p for p in Cart.objects.all() if p.user == request.user]
            if cart_product:
                for p in cart_product:
                    amount = amount + (p.quantity * p.product.discounted_price)
            total_amount = amount + shipping_amount

            data = {
                'quantity':c.quantity,
                'amount':amount,
                'totalamount':total_amount
            }
            return JsonResponse(data)

def remove_cart(request):
    if request.method == 'GET':
        prod_id = request.GET['prod_id']
        c = Cart.objects.get(Q(product=prod_id) & Q(user=request.user))
        c.delete()
        amount = 0.0
        shipping_amount = 70.0
        total_amount = 0.0
        cart_product = [p for p in Cart.objects.all() if p.user == request.user]
        if cart_product:
            for p in cart_product:
                amount = amount + (p.quantity * p.product.discounted_price)
        total_amount = amount + shipping_amount

        data = {

            'amount':amount,
            'totalamount':total_amount
        }
        return JsonResponse(data)



def buy_now(request):
 return render(request, 'app/buynow.html')

@method_decorator(login_required, name='dispatch')
class ProfileView(View):
    def get(self, request):
        form = CustomerProfileForm()
        return render(request, 'app/profile.html', {'form':form, 'active':'btn-primary'})

    def post(self, request):
        form = CustomerProfileForm(request.POST)
        
        if form.is_valid():
            user  = request.user
            name = form.cleaned_data['name']
            locality = form.cleaned_data['locality']
            city = form.cleaned_data['city']
            state = form.cleaned_data['state']
            zipcode = form.cleaned_data['zipcode']
            save_form_data = Customer(user=user ,name=name, city=city, locality=locality, state=state, zipcode=zipcode)
            save_form_data.save()
            messages.success(request, 'Congrats!! Profile has been updated ')
        return render(request, 'app/profile.html', {'form':form, 'active':'btn-primary'})

@login_required
def address(request):
    addresses = Customer.objects.filter(user=request.user)
    return render(request, 'app/address.html', {'addresses':addresses, 'active':'btn-primary'})

@login_required
def orders(request):
    order_placed = OrderPlaced.objects.filter(user=request.user)
    return render(request, 'app/orders.html', {'order_placeds':order_placed})

@login_required
def change_password(request):
    return render(request, 'app/changepassword.html')

@cache_page(CACHE_TTL)
def laptop(request, data=None):
    laptops = []
    if data == 'all':
        laptops = Product.objects.filter(category='L')
    elif data == 'Lenovo' or data == 'Acer':
        laptops = Product.objects.filter(category='L').filter(brand = data)
    elif data == 'Below':
        laptops = Product.objects.filter(category='L').filter(discounted_price__lt = 100000)
    elif data == 'Above':
        laptops = Product.objects.filter(category='L').filter(discounted_price__gt = 100000)
    return render(request, 'app/laptop.html', {"laptops":laptops})

# def login(request):           # Not needed
#  return render(request, 'app/login.html')

class CustomerRegistrationView(View):
    def get(self, request):
        form = CustomerRegistrationForm()
        return render(request, 'app/customerregistration.html', {'form':form})

    def post(self,request):
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            messages.success(request, f'Congratulations!! Registered successfully.')
            form.save()
            
        return render(request, 'app/customerregistration.html', {'form':form})        

@login_required
def checkout(request):
    user = request.user
    addresses = Customer.objects.filter(user=user)
    cart_items = Cart.objects.filter(user=user)
    amount = 0.0
    shipping_amount = 70.0
    cart_product = [p for p in Cart.objects.all() if p.user == request.user]
    if cart_product:
        for p in cart_product:
            amount = amount + (p.quantity * p.product.discounted_price)
    total_amount = amount + shipping_amount
    return render(request, 'app/checkout.html', {'addresses':addresses, 'total_amount':total_amount, 'cart_items':cart_items})

@login_required
def payment_done(request):
    if request.method == "GET":
        user = request.user
        custid = request.GET.get('custid')
        customer = Customer.objects.get(id=custid)
        cart = Cart.objects.filter(user=user)
        for c in cart:
            OrderPlaced(user=user, customer=customer, product=c.product, quantity=c.quantity).save()
            c.delete()
    return redirect("/orders/")

def password_reset_request(request):
	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = User.objects.filter(Q(email=data))
			if associated_users.exists():
				for user in associated_users:
					subject = "Password Reset Requested"
					email_template_name = "app/password-reset/password_reset_email.txt"
					c = {
					"email":user.email,
					'domain':'127.0.0.1:8000',
					'site_name': 'Website',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					"user": user,
					'token': default_token_generator.make_token(user),
					'protocol': 'http',
					}
					email = render_to_string(email_template_name, c)
					try:
						send_mail(subject, email, 'nvidda257605@gmail.com' , [user.email], fail_silently=False)
					except BadHeaderError:
						return HttpResponse('Invalid header found.')
					return redirect ("/password-reset/done/")
        
	
	return render(request=request, template_name="app/password-reset/password_reset.html", context={"form":MyPasswordResetForm})
