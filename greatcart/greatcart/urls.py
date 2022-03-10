
from django.contrib import admin
from django.urls import path,include
from . import views

from django.conf.urls.static import static
from django.conf import settings

from django.views.static import serve
from django.conf.urls import url

urlpatterns = [
    path('admin/', include('admin_honeypot.urls',namespace='admin_honeypot')),
    path('securelogin/', admin.site.urls),
    path('', views.home,name='home'),
    path('store/', include('store.urls')),
    path('cart/', include('carts.urls')),
    path('accounts/', include('accounts.urls')),
    path('orders/', include('orders.urls')),

    # helps to serve media files when DEBUG=False
    url(r'^media/(?P<path>.*)$', serve,{'document_root':  settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),

]+ static(settings.MEDIA_URL ,document_root=settings.MEDIA_ROOT)
