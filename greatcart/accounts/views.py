from django.shortcuts import render,redirect
from django.contrib import messages,auth
from django.http import HttpResponseRedirect,HttpResponse
from django.contrib.auth.decorators import login_required

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
			auth.login(request,user)
			messages.add_message(request,messages.SUCCESS,'You are now logged in.')
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
	return render(request, 'accounts/dashboard.html')