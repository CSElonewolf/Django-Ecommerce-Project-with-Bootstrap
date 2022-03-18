from django import forms
from django.core.exceptions import ValidationError

from .models import Account, UserProfile

class RegistrationForm(forms.ModelForm):
	# add 2 extra fields with class and placeholder
	password = forms.CharField(widget = forms.PasswordInput(attrs={
		'placeholder':'Enter Password',
		'class': 'form-control'
		}))
	confirm_password = forms.CharField(widget = forms.PasswordInput(attrs={
		'placeholder':'Confirm Password',
		'class': 'form-control'
		}))

	# fields to include in the register form form the models
	class Meta:
		model = Account
		fields = ['first_name','last_name','email','phone_number']

	def __init__(self,*args,**kwargs):
		super(RegistrationForm,self).__init__(*args,**kwargs)
		# adding placeholders for various fields in the form
		self.fields['first_name'].widget.attrs['placeholder'] = 'Enter First Name'
		self.fields['last_name'].widget.attrs['placeholder'] = 'Enter Last Name'
		self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter Phone Number'
		self.fields['email'].widget.attrs['placeholder'] = 'Enter Email'

		# loop through all the fields and add class
		for field in self.fields:
			self.fields[field].widget.attrs['class'] = 'form-control'

	# check if the password and confirm password match or not
	def clean(self):
		cleaned_data = super(RegistrationForm,self).clean()
		password = cleaned_data.get('password')
		confirm_password = cleaned_data.get('confirm_password')

		if password != confirm_password:
			raise ValidationError("Password doesn't match")

# forms for the Edit Profile section inside dashboard
class UserForm(forms.ModelForm):
	class Meta:
		model = Account
		fields = ('first_name','last_name','phone_number','email')

	def __init__(self,*args,**kwargs):
		super(UserForm,self).__init__(*args,**kwargs)

		# loop through all the fields and add class
		for field in self.fields:
			self.fields[field].widget.attrs['class'] = 'form-control'

class UserProfileForm(forms.ModelForm):
	# to remove -"Profile Picture Currently: userprofile/drf-cbv.jpg" message on the image tag we use this
	profile_picture = forms.ImageField(required=False,error_messages={'invalid':{"'Image files only"}}, widget = forms.FileInput)


	class Meta:
		model = UserProfile
		fields=('address_line_1','address_line_2','city','state','country','profile_picture')

	def __init__(self,*args,**kwargs):
		super(UserProfileForm,self).__init__(*args,**kwargs)

		# loop through all the fields and add class
		for field in self.fields:
			self.fields[field].widget.attrs['class'] = 'form-control'