from django import forms
from .models import Order


class OrderForm(forms.ModelForm):
	class Meta:
		model = Order
		fields =['first_name', 'last_name', 'phone','email', 'address_line_1','address_line_2','country','city','state','order_note']

		# if we wish to pre populate the data in checkout pagefrom Account  model we can use this form instead
		# fields =['address_line_1','address_line_2','country','city','state','order_note']