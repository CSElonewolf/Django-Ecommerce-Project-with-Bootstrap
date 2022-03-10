from django.shortcuts import render,get_object_or_404,redirect
from django.core.paginator import EmptyPage,PageNotAnInteger,Paginator
from django.db.models import Q
from django.contrib import messages

# import from the app itself
from .models import Product, ProductGallery
from category.models import Category
from .models import ReviewRating
from .forms import ReviewForm
from orders.models import OrderProduct

# model imports from another app
from carts.models import CartItem
from carts.views import _cart_id


# Create your views here.
def store(request,category_slug=None):

	categories = None
	products = None
	# display products for specific category
	if category_slug != None:
		categories = get_object_or_404(Category,slug = category_slug)
		products = Product.objects.filter(category = categories,is_available = True).order_by('id')
		# pagination
		paginator = Paginator(products,3)
		page = request.GET.get('page')
		paged_products = paginator.get_page(page)

		product_count = products.count()
	# display all the products inside the Products table
	else:
		products = Product.objects.all().filter(is_available = True).order_by('id')
		# pagination
		paginator = Paginator(products,3)
		page = request.GET.get('page')
		paged_products = paginator.get_page(page)
		product_count = products.count()

	context = {
		'products': paged_products,
		'product_count':product_count,
		'categories':categories
	}
	return render(request,'store/store.html',context)

# function to search product
def search(request):
	if 'keyword' in request.GET:
		keyword = request.GET['keyword']
		if keyword:
			products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains = keyword))
			# pagination
			paginator = Paginator(products,3)
			page = request.GET.get('page')
			paged_products = paginator.get_page(page)
			product_count = products.count()
	context = {
		'products':paged_products,
		'product_count':product_count,
	}
	return render(request,'store/store.html',context)


# get the product details
def product_detail(request,category_slug,product_slug):
	try:
		single_product = Product.objects.get(category__slug = category_slug,slug = product_slug)
		
		# check if the product is already added to cart or not
		in_cart = CartItem.objects.filter(cart__cart_id = _cart_id(request),product = single_product)
	except Exception as e:
		raise e

	# check if the logged in user is authorized to submit a review or not
	if request.user.is_authenticated:
		try:
			orderproduct = OrderProduct.objects.filter(user = request.user, product_id = single_product.id).exists()
		except:
			orderproduct = None
	else:
		orderproduct = None

	# get review for the product
	reviews = ReviewRating.objects.filter(product_id = single_product.id, status = True)

	product_gallery = ProductGallery.objects.filter(product_id=single_product.id)

	context = {
		'single_product': single_product,
		'in_cart': in_cart,
		'orderproduct':orderproduct,
		'reviews': reviews,
		'product_gallery':product_gallery
	}

	return render(request,'store/product_detail.html',context)

def submit_review(request,product_id):
	url = request.META.get('HTTP_REFERER')
	print(url)
	if request.method == "POST":
		# updates the old review fromo the user
		try:
			reviews = ReviewRating.objects.get(user__id = request.user.id, product__id = product_id)
			form = ReviewForm(request.POST,instance = reviews)
			form.save()
			messages.add_message(request,messages.SUCCESS,'Thank You! your review have been updated.')
			return redirect(url)
		# helps in adding a new review
		except ReviewRating.DoesNotExist:
			form = ReviewForm(request.POST)
			if form.is_valid():
				data = ReviewRating()
				data.subject = form.cleaned_data['subject']
				data.rating = form.cleaned_data['rating']
				data.review = form.cleaned_data['review']
				data.ip = request.META.get('REMOTE_ADDR')
				data.product_id = product_id
				data.user_id = request.user.id
				data.save()
				messages.add_message(request,messages.SUCCESS,'Thank you! Your review has been submitted.')
				return redirect(url)
