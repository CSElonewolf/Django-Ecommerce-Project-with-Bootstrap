# imports from thr Django
from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
import datetime
import json
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

# imports from the project
from .forms import OrderForm
from carts.models import CartItem
from .models import Order,Payment,OrderProduct
from store.models import Product


def payments(request):
# grab the payments details sent from payments.html
	body = json.loads(request.body)
	order = Order.objects.get(user = request.user,is_ordered = False,order_number = body['orderId'])

	payment = Payment(
		user = request.user,
		payment_id = body['transId'],
		payment_method = body['payment_method'],
		amount_paid = order.order_total,
		status = body['status'],
	)
	# save data inside the Payments models
	payment.save()

	#save the paymet details inside the order model
	order.payment  = payment
	order.is_ordered = True
	order.save()

	# Tasks that are need to be completed
	# --------------------------------------------
	# 1. Move the cart items to Order Product Table
	cart_items = CartItem.objects.filter(user = request.user)

	for item in cart_items:
		orderproduct = OrderProduct()
		orderproduct.order_id = order.id
		orderproduct.payment  = payment
		orderproduct.user_id = request.user.id
		orderproduct.product_id = item.product.id
		orderproduct.quantity = item.quantity
		orderproduct.product_price = item.product.price
		orderproduct.ordered = True
		orderproduct.save()


		# save the variation of the product items
		cart_item = CartItem.objects.get(id = item.id)
		product_variation = cart_item.variations.all()
		orderproduct = OrderProduct.objects.get(id = orderproduct.id)
		orderproduct.variations.set(product_variation)
		orderproduct.save()

		# 2. Reduce the quantity of the sold product
		product = Product.objects.get(id = item.product.id)
		product.stock -= item.quantity
		product.save()

	# 3. Clear cart
	CartItem.objects.filter(user = request.user).delete()

	# 4. Send order recieved email to the customer
	mail_subject = 'Thank you for shopping with greatcart'
	message = render_to_string('orders/order_recieved_email.html',{
		'user': request.user,
		'order':order
	})
	to_email = request.user.email
	send_email = EmailMessage(mail_subject,message, to =[to_email])
	send_email.send()

	# 5. send order number and transaction id back to sendData method in payments.html page via JsonResponse
	data = {
		'order_number':order.order_number,
		'transID':payment.payment_id
	}
	return JsonResponse(data)

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

# view that passes the ordered product details to the payment successful page
def order_complete(request):
	order_number = request.GET.get('order_number')
	transID = request.GET.get('payment_id')

	try:
		# grab the ordered product
		order = Order.objects.get(order_number = order_number, is_ordered = True)

		ordered_products = OrderProduct.objects.filter(order_id = order.id)

		# calculate the sub_total
		sub_total = 0
		for i in ordered_products:
			sub_total += i.product_price * i.quantity

		# grab the payment model object
		payment = Payment.objects.get(payment_id = transID)

		context = {
			'order':order,
			'ordered_products':ordered_products,
			'order_number':order.order_number,
			'transID': payment.payment_id,
			'payment':payment,
			'subtotal': sub_total
		}
		return render(request, 'orders/order_complete.html',context)

	except (Payment.DoesNotExist,Order.DoesNotExist):
		return redirect('home')
