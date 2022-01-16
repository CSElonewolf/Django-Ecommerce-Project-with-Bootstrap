from django.contrib import admin
import admin_thumbnails
from .models import Product,Variation,ReviewRating,ProductGallery
# Register your models here.

# display the product image from the ProductGallery
@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
	model = ProductGallery
	extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ('product_name','price','stock','category','modified_date','is_available')

	prepopulated_fields = {'slug':('product_name',)}
	inlines =  [ProductGalleryInline]


# to set the size and color of different product in the amdin panel
@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
	list_display = ('product','variation_category','variation_value','is_active')
	list_editable = ('is_active',)
	list_filter = ('product','variation_category','variation_value','is_active')


admin.site.register(ReviewRating)
admin.site.register(ProductGallery)