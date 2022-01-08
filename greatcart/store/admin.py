from django.contrib import admin
from .models import Product,Variation,ReviewRating
# Register your models here.

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
	list_display = ('product_name','price','stock','category','modified_date','is_available')

	prepopulated_fields = {'slug':('product_name',)}


# to set the size and color of different product in the amdin panel
@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
	list_display = ('product','variation_category','variation_value','is_active')
	list_editable = ('is_active',)
	list_filter = ('product','variation_category','variation_value','is_active')


admin.site.register(ReviewRating)