# imports from thr Django
from django.shortcuts import render,redirect
from django.http import HttpResponse
import datetime
import json

# imports from the project
from .forms import OrderForm
from carts.models import CartItem
from .models import Order
from .models import Payment


def payments(request):
	body = json.loads(request.body)
	order = Order.objects.get(user = request.user,is_ordered = False,order_number = body['orderId'])
	payment = Payment(
		user = request.user,
		payment_id = body['transId'],
		payment_method = body['payment_method'],
		amount_paid = order.order_total,
		status = body['status'],
	)
	payment.save()

	order.payment  = payment
	order.is_ordered = True
	order.save()


	return render(request, 'orders/payments.html')

# Create your views here.
def place_order(request,total=0,quantity = 0,):
	current_user = request.user

	cart_items = CartItem.objects.filter(user = current_user)
	cart_count = cart_items.count()
	if cart_count <= 0:
		return redirect('store')

	# loop through products inside cart and calculate the grand total
	grand_total = 0
	tax = 0
	for cart_item in cart_items:
		total += cart_item.product.price*cart_item.quantity
		quantity +=cart_item.quantity

	# calculate the tax and grand total
	tax = (18*total) /100
	grand_total = total + tax

	if request.method == "POST":
		form = OrderForm(request.POST)
		if form.is_valid():
			data = Order()

			data.user = current_user
			data.first_name = form.cleaned_data['first_name']
			data.last_name = form.cleaned_data['last_name']
			data.phone = form.cleaned_data['phone']
			data.email = form.cleaned_data['email']
			data.address_line_1 = form.cleaned_data['address_line_1']
			data.address_line_2 = form.cleaned_data['address_line_2']
			data.country = form.cleaned_data['country']
			data.city = form.cleaned_data['city']
			data.state = form.cleaned_data['state']
			data.order_note = form.cleaned_data['order_note']
			data.order_total = grand_total
			data.tax = tax
			data.ip  = request.META.get('REMOTE_ADDR')
			data.save()

			# generate the order number
			yr = int(datetime.date.today().strftime('%Y'))
			dt = int(datetime.date.today().strftime('%d'))
			mt = int(datetime.date.today().strftime('%m'))

			# let's say today is 10th Jan,2022
			# so current_date = 20220110
			d = datetime.date(yr,mt,dt)
			current_date = d.strftime('%Y%m%d')
			#  now the order_number is going to be like = 20220110[1]
			# [1] is data.id
			order_number = current_date + str(data.id)
			data.order_number = order_number
			data.save()

			order = Order.objects.get(user = current_user,is_ordered = False,order_number = order_number)
			context = {
				'order':order,
				'cart_items':cart_items,
				'total':total,
				'tax':tax,
				'grand_total':grand_total

			}

			return render(request, 'orders/payments.html',context)

	else:
		return redirect('checkout')
