from django.shortcuts import render, reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.forms import ValidationError
from django.views.generic import ListView, TemplateView
from .models import CartItem
from catalog.models import Book, Category
from catalog.views import add_categories_to_context, add_total_books
from .cartutils import is_cart_id_session_set, _set_or_get_session_id, get_cart_items, get_cart_id_session
from .cartutils import  get_cart_item_of_book, article_already_in_cart, get_cart_counter, _remove_cart_item


def add_cart_counter_to_context(request, ctx):
    ctx['cart_counter'] = get_cart_counter(request)
    return ctx

def add_cart_item(request, pk):
    if request.method == 'POST':
        book = Book.objects.get(pk=pk)
        cart_items = get_cart_items(request)
        if article_already_in_cart(cart_items, book):
            cart_item = get_cart_item_of_book(cart_items, book)
            cart_item.augment_quantity(1)
            cart_item.save()
        else:
            cart_item = CartItem()
            cart_item.cart_id = _set_or_get_session_id(request)
            cart_item.book = book
            cart_item.quantity = 1
            cart_item.save()
        url_redirect = reverse('cart:cart_content')
        return HttpResponseRedirect(url_redirect)
    else:
        pass

def remove_cart_item(request, pk):
    if request.method == 'POST':
        book = Book.objects.get(pk=pk)
        _remove_cart_item(request, book)
        url_redirect = reverse('cart:cart_content')
        return HttpResponseRedirect(url_redirect)
    else:
        raise ValueError('Should not be called with GET')


# This import must be defined here, after the functions definition and not before,
# otherwise it fails.


class CartView(ListView):
    model = CartItem
    template_name = 'cart/cart_content.html'
    context_object_name = 'cart'

    def get_queryset(self):
        if is_cart_id_session_set(self.request):
            return CartItem.objects.filter(cart_id = get_cart_id_session(self.request))
        else:
            return []

    def get_context_data(self, **kwargs):
        ctx = super(CartView, self).get_context_data(**kwargs)
        ctx = add_categories_to_context(ctx)
        ctx = add_cart_counter_to_context(self.request, ctx)
        ctx = add_total_books(ctx)
        if  is_cart_id_session_set(self.request):
            cart_id = get_cart_id_session(self.request)
            ctx['cart_total'] = CartItem.get_total_of_cart(cart_id)
            return ctx
        else:
            return ctx


class CheckoutView(TemplateView):
    template_name = 'cart/checkout.html'

    def get_context_data(self, **kwargs):
        ctx = super(CheckoutView, self).get_context_data(**kwargs)
        ctx = add_categories_to_context(ctx)
        ctx = add_cart_counter_to_context(self.request, ctx)
        ctx = add_total_books(ctx)
        if  is_cart_id_session_set(self.request):
            cart_id = get_cart_id_session(self.request)
            ctx['cart_total'] = CartItem.get_total_of_cart(cart_id)
            return ctx
        else:
            return ctx


