# django inner file imports
from django.db.models import query
from django.shortcuts import render,redirect
from django.contrib import messages,auth
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.decorators import login_required
import requests


# verification email imports
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator

# project imports
from .forms import RegistrationForm
from .models import Account
from carts.models import Cart,CartItem
from carts.views import _cart_id
from orders.models import Order
# Create your views here.
def register(request):
	if request.method == 'POST':
		form = RegistrationForm(request.POST)
		if form.is_valid():
			# collecing vital information for registration
			first_name = form.cleaned_data['first_name']
			last_name = form.cleaned_data['last_name']
			email = form.cleaned_data['email']
			phone_number = form.cleaned_data['phone_number']
			username = email.split('@')[0]
			password = form.cleaned_data['password']
			user = Account.objects.create_user(first_name=first_name,last_name=last_name,email=email,password=password,username=username)
			user.phone_number = phone_number
			user.save()

			# USER ACTIVATION email sending
			current_site = get_current_site(request)
			mail_subject = 'Please activate your account'
			message = render_to_string('accounts/account_verification_email.html',{
				'user':user,
				'domain':current_site,
				'uid':urlsafe_base64_encode(force_bytes(user.pk)),
				'token':default_token_generator.make_token(user)
			})
			to_email = email
			send_email = EmailMessage(mail_subject,message,to=[to_email])
			send_email.send()

			# redirects to the info page
			return redirect(f'/accounts/login/?command=verification&email={email}')
	else:
		form = RegistrationForm()
	context = {
		'form':form
	}
	return render(request, 'accounts/register.html',context)


def login(request):
	if request.method == 'POST':
		email = request.POST['email']
		password = request.POST['password']

		# authenticate with email and passowrd
		user = auth.authenticate(email = email,password = password)

# if it is valid user then login and redirect to dashboard
		if user is not None:
			try:
				cart = Cart.objects.get(cart_id = _cart_id(request))
				is_cart_item_exists = CartItem.objects.filter(cart = cart).exists()
				if is_cart_item_exists:
					cart_item = CartItem.objects.filter(cart = cart)

					product_variation = []
					# get the variations from of the cart item
					for item in cart_item:
						variation = item.variations.all()
						product_variation.append(list(variation))

					cart_item = CartItem.objects.filter(user = user)
					ex_var_list = []
					id = []
					for item in cart_item:
						existing_variations = item.variations.all()
						ex_var_list.append(list(existing_variations))
						id.append(item.id)

					for pr in product_variation:
						if pr in ex_var_list:
							index = ex_var_list.index(pr)
							item_id = id[index]
							item = CartItem.objects.get(id = item_id)
							item.quantity +=1
							item.user = user
							item.save()
						else:
							cart_item = CartItem.objects.filter(cart = cart)
							for item in cart_item:
								item.user = user
								item.save()

			except:
				pass

			auth.login(request,user)
			messages.add_message(request,messages.SUCCESS,'You are now logged in.')


			# redirects to checkout page after login if the any user wish to buy items in cart when not logged in
			url = request.META.get('HTTP_REFERER')
			try:
				query = requests.utils.urlparse(url).query
				params = dict(x.split('=') for x in  query.split('&'))
				if 'next' in params:
					nextPage = params['next']
					return redirect(nextPage)
			except:
				return redirect('dashboard')
		else:
			messages.add_message(request,messages.ERROR,'Invalid Login Credentials')
			return redirect('login')

	return render(request, 'accounts/login.html')

# logout
@login_required(login_url='login')
def logout(request):
	auth.logout(request)
	messages.add_message(request,messages.SUCCESS,'Logged Out')
	return redirect('login')

# method that handles the verification from the link emailed during registration
def activate(request,uidb64,token):
	# finds user with unique id
	try:
		uid = urlsafe_base64_decode(uidb64).decode()
		user = Account._default_manager.get(pk = uid)

	except(TypeError, ValueError,OverflowError,Account.DoesNotExist):
		user = None

	# checks the token generated during registration
	if user is not None and default_token_generator.check_token(user,token):
		user.is_active = True
		user.save()
		messages.add_message(request,messages.SUCCESS,'Congratulation! Your account is activated')
		return redirect('login')
	else:
		messages.add_message(request,messages.ERROR,'Invalid activation link')
		return redirect('register')



@login_required(login_url='login')
def dashboard(request):
	orders = Order.objects.order_by("-created_at").filter(user_id=request.user.id, is_ordered=True)
	orders_count = orders.count()

	context = {
		'orders_count':orders_count
	}
	return render(request, 'accounts/dashboard.html',context)


def my_orders(request):
	orders = Order.objects.filter(user=request.user, is_ordered= True).order_by('-created_at')
	context = {
		'orders':orders
	}
	return render(request,'accounts/my_orders.html',context)


# forgot password view
def forgotPassword(request):
	if request.method == "POST":
		email = request.POST['email']
		if Account.objects.filter(email=email).exists():
			user = Account.objects.get(email__exact = email)

			current_site = get_current_site(request)
			mail_subject = 'Reset Your Password'
			message = render_to_string('accounts/reset_password_email.html',{
				'user':user,
				'domain':current_site,
				'uid':urlsafe_base64_encode(force_bytes(user.pk)),
				'token':default_token_generator.make_token(user)
			})

			to_email = email
			send_email = EmailMessage(mail_subject,message,to=[to_email])
			send_email.send()

			messages.add_message(request,messages.SUCCESS,'Password reset email has been sent to your email address')
			return redirect('login')

		else:
			messages.add_message(request,messages.ERROR,'Account does not exist')
			return redirect('forgotPassword')

	return render(request,'accounts/forgotPassword.html')

def resetpassword_validate(request,uidb64,token):
	try:
		uid = urlsafe_base64_decode(uidb64).decode()
		user = Account._default_manager.get(pk = uid)

	except(TypeError, ValueError,OverflowError,Account.DoesNotExist):
		user = None

	# checks the token generated during registration
	if user is not None and default_token_generator.check_token(user,token):
		request.session['uid'] = uid
		messages.add_message(request,messages.SUCCESS,'Please reset your password')
		return redirect('resetPassword')
	else:
		messages.add_message(request,messages.ERROR,'This link is expired')
		return redirect('login')


def resetPassword(request):
	if request.method == 'POST':
		if request.session.get('uid') is not None:
			password = request.POST['password']
			confirm_password = request.POST['confirm_password']

			if password == confirm_password:
				uid = request.session.get('uid')
				user = Account.objects.get(pk = uid)
				user.set_password(password)
				user.save()
				request.session.delete('uid')
				messages.add_message(request,messages.SUCCESS,'Password reset succesfully')
				return redirect('login')

			else:
				messages.add_message(request,messages.ERROR,"Password didn't match")
				return redirect('resetPassword')
		else:
			return redirect('forgotPassword')

	else:
		return render(request,'accounts/resetPassword.html')


def edit_profile(request):
	return render(request,'accounts/edit_profile.html')