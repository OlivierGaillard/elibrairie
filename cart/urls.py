from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from . import views


app_name = 'cart'

urlpatterns = [
    url(r'^add_item/(?P<pk>[0-9]+)$', views.add_cart_item, name='add_item'),
    url(r'^cart_content/$', views.CartView.as_view(), name='cart_content'),
    url(r'^checkout/$', views.CheckoutView.as_view(), name='checkout'),
    url(r'^remove_item/(?P<pk>[0-9]+)$', views.remove_cart_item, name='remove_item'),
    ]