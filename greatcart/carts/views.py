from django.shortcuts import render,redirect,get_object_or_404
from store.models import Product
from .models import Cart,CartItem
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
# Create your views here.

# obtains the cart id = session_key
def _cart_id(request):
	cart = request.session.session_key
	print(cart)
	if not cart:
		cart = request.session.create()
	return cart


# add item in the cart
def add_cart(request,product_id):
	# get the product using the product_id
	product = Product.objects.get(id = product_id)
	try:
		# get the cart_id present in the seesion
		cart = Cart.objects.get(cart_id = _cart_id(request))
	except Cart.DoesNotExist:
		cart = Cart.objects.create(
			cart_id = _cart_id(request)
		)
	cart.save()

	try:
		cart_item = CartItem.objects.get(product = product,cart = cart)
		cart_item.quantity +=1
		cart_item.save()

	except CartItem.DoesNotExist:
		cart_item = CartItem.objects.create(
			product = product,
			quantity = 1,
			cart = cart,
		)
		cart_item.save()
	# return HttpResponse(cart_item.product.product_name)
	return redirect('cart')

# remove/decreament the product quantity
def remove_cart(request,product_id):
	cart = Cart.objects.get(cart_id = _cart_id(request))
	product = get_object_or_404(Product,id = product_id)
	cart_item = CartItem.objects.get(product=product,cart = cart)
	if cart_item.quantity > 1:
		cart_item.quantity -=1
		cart_item.save()
	else:
		cart_item.delete()
	return redirect('cart')

def remove_cart_item(request,product_id):
	cart = Cart.objects.get(cart_id = _cart_id(request))
	product = get_object_or_404(Product,id = product_id)
	cart_item = CartItem.objects.get(product=product,cart = cart)
	cart_item.delete()
	return redirect('cart')




# Info to be displayed in the cart page
def cart(request,total=0,quantity = 0,cart_items = None):
	try:
		tax = 0
		grand_total = 0
		cart = Cart.objects.get(cart_id = _cart_id(request))
		cart_items = CartItem.objects.filter(cart = cart,is_active = True)
		for cart_item in cart_items:
			total += cart_item.product.price*cart_item.quantity
			quantity +=cart_item.quantity

		tax = (18*total) /100
		grand_total = total + tax

	except cart.ObjectDoesNotExist:
		pass

	context = {
		'total':total,
		'quantity':quantity,
		'cart_items':cart_items,
		'tax':round(tax),
		'grand_total': round(grand_total),
	}

	return render(request,'store/cart.html',context)