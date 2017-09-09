from django.test import TestCase, Client
from django.contrib.staticfiles import finders
from django.shortcuts import reverse
import os
from django.http import request
from elibrairie import settings
from catalog.models import Book, Category
from .models import CartItem
from .cartutils import CART_ID_SESSION_KEY

class TestCart(TestCase):

    fixtures = ['category.json', 'books.json']

    def test_additem(self):
        cart_item = CartItem()
        cart_item.book = Book.objects.get(pk=1)
        cart_item.cart_id = 'toto-cart'
        cart_item.save()

        cart_item2 = CartItem()
        cart_item2.book = Book.objects.get(pk=2)
        cart_item2.cart_id = 'toto-cart'
        cart_item2.save()

        self.assertTrue(len(CartItem.objects.all()) > 0)


    def test_session(self):
        session = self.client.session
        session['toto'] = 'session-toto'
        session.save()
        self.assertTrue(session['toto'])
        session.set_test_cookie()
        self.assertTrue(session.test_cookie_worked())
        session.delete_test_cookie()



    def test_additem_url(self):
        add_item_url = reverse('cart:add_item', kwargs={'pk':1})
        self.assertEqual(add_item_url, '/cart/add_item/1')

    def test_article_added_in_cart(self):
        c = Client()
        book = Book.objects.get(titre='Un paradigme')
        add_item_url = reverse('cart:add_item', kwargs={'pk': book.pk})
        response = c.post(add_item_url, follow=True) # The view makes a HttpResponseRedirect
        self.assertEqual(response.status_code, 200)  # Without 'follow=True' we get 302
        cart_item = CartItem.objects.first()
        self.assertEqual(cart_item.book, book)


    def test_session_id_stored_after_article_added(self):
        """ Verify that session-ID is generated."""
        c = Client()
        book = Book.objects.get(titre='Un paradigme')
        add_item_url = reverse('cart:add_item', kwargs={'pk': book.pk})
        response = c.post(add_item_url, follow=True)
        self.assertEqual(response.status_code, 200)
        cart_item = CartItem.objects.first()
        self.assertTrue(len(cart_item.cart_id) > 0)

    def test_user_add_2_articles(self):
        c = Client()
        book1 = Book.objects.get(titre='Un paradigme')
        add_item_url = reverse('cart:add_item', kwargs={'pk': book1.pk})
        c.post(add_item_url, follow=True)
        book2 = Book.objects.get(titre='Toujours mieux!')
        add_item_url = reverse('cart:add_item', kwargs={'pk': book2.pk})
        response = c.post(add_item_url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CartItem.objects.all().count(), 2)

    def test_adding_same_article_2_times(self):
        c = Client()
        book1 = Book.objects.get(titre='Un paradigme')
        add_item_url = reverse('cart:add_item', kwargs={'pk': book1.pk})
        c.post(add_item_url, follow=True)
        c.post(add_item_url, follow=True)
        self.assertEqual(1, CartItem.objects.count())
        self.assertEqual(2, CartItem.objects.first().quantity)

    def test_cart_total(self):
        "Return the cart total"
        c = Client()
        book1 = Book.objects.get(titre='Un paradigme')
        book1_price = book1.prix
        add_item_url = reverse('cart:add_item', kwargs={'pk': book1.pk})
        c.post(add_item_url, follow=True)
        book2 = Book.objects.get(titre='Toujours mieux!')
        book2_price = book2.prix
        add_item_url = reverse('cart:add_item', kwargs={'pk': book2.pk})
        c.post(add_item_url, follow=True)
        self.assertEqual(CartItem.get_total_of_cart(c.session[CART_ID_SESSION_KEY]), book1_price + book2_price)

    def test_cart_total_same_article_2_times(self):
        c = Client()
        book1 = Book.objects.get(titre='Un paradigme')
        add_item_url = reverse('cart:add_item', kwargs={'pk': book1.pk})
        c.post(add_item_url, follow=True)
        c.post(add_item_url, follow=True)
        self.assertEqual(CartItem.get_total_of_cart(c.session[CART_ID_SESSION_KEY]), book1.prix * 2)

    def test_list_of_categories_available(self):
        c = Client()
        all_books_url = '/catalog/listall/'
        response = c.get(all_books_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('/catalog/listcat/', response.content.decode(),
                      'No link to book categories found in all books page.')

    def test_list_of_categories_available_within_cart_content_page(self):
        c = Client()
        book = Book.objects.get(titre='Un paradigme')
        add_item_url = reverse('cart:add_item', kwargs={'pk': book.pk})
        response = c.post(add_item_url, follow=True)
        self.assertIn('/catalog/listcat/', response.content.decode(), 'No link to book categories found in cart content page.')

    def test_nb_items_in_cart_visible_on_homepage(self):
        c = Client()
        response = c.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('counter">0<', response.content.decode())

    def test_nb_items_in_cart_visible_on_cart_content_page(self):
        c = Client()
        response = c.get('/cart/cart_content/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('counter">0<', response.content.decode())

    def test_nb_items_in_cart_visible_on_all_book_page(self):
        c = Client()
        response = c.get('/catalog/listall/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('counter">0<', response.content.decode())



    def test_nb_items_in_cart_visible_on_bd_category(self):
        c = Client()
        u = '/catalog/listcat/BD'
        response = c.get(u)
        self.assertEqual(response.status_code, 200)
        self.assertIn('counter">0<', response.content.decode())

    def test_nb_items_in_cart_visible_on_book_detail(self):
        c = Client()
        u = '/catalog/detail/6'
        response = c.get(u)
        self.assertEqual(response.status_code, 200)
        self.assertIn('counter">0<', response.content.decode())


    def test_remove_link_visible_in_detail_page(self):
        c = Client()
        book = Book.objects.get(titre='Un paradigme')
        add_item_url = reverse('cart:add_item', kwargs={'pk': book.pk})
        response = c.post(add_item_url, follow=True)
        self.assertEqual(response.status_code, 200)  # Without 'follow=True' we get 302
        u = '/catalog/detail/%s' % book.pk
        response = c.get(u)
        self.assertEqual(response.status_code, 200)
        self.assertIn('remove', response.content.decode())

    def test_remove_link_visible_in_cart_page(self):
        c = Client()
        book = Book.objects.get(titre='Un paradigme')
        add_item_url = reverse('cart:add_item', kwargs={'pk': book.pk})
        response = c.post(add_item_url, follow=True)
        self.assertEqual(response.status_code, 200)  # Without 'follow=True' we get 302
        u = '/cart/cart_content/'
        response = c.get(u)
        self.assertEqual(response.status_code, 200)
        self.assertIn('remove', response.content.decode())

    def test_remove_item_from_cart(self):
        c = Client()
        book = Book.objects.get(titre='Un paradigme')
        add_item_url = reverse('cart:add_item', kwargs={'pk': book.pk})
        response = c.post(add_item_url, follow=True)
        self.assertEqual(response.status_code, 200)  # Without 'follow=True' we get 302
        self.assertEqual(1, CartItem.objects.count())
        u = '/catalog/detail/%s' % book.pk
        response = c.get(u)
        self.assertEqual(response.status_code, 200)
        self.assertIn('remove', response.content.decode())
        remove_item_url = reverse('cart:remove_item', kwargs={'pk': book.pk})
        response = c.post(remove_item_url, follow=True)
        self.assertEqual(response.status_code, 200)  # Without 'follow=True' we get 302
        self.assertEqual(0, CartItem.objects.count())

    def test_remove_item_from_empty_cart(self):
        '''Insure no removal if cart is already empty'''
        c = Client()
        book = Book.objects.get(titre='Un paradigme')
        u = '/catalog/detail/%s' % book.pk
        response = c.get(u)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('remove', response.content.decode())
        remove_item_url = reverse('cart:remove_item', kwargs={'pk': book.pk})
        response = c.post(remove_item_url, follow=True)
        self.assertEqual(response.status_code, 200)  # Without 'follow=True' we get 302
        self.assertEqual(0, CartItem.objects.count())

    def test_remove_button_hidden_if_cart_empty_in_page_detail(self):
        '''Insure remove button is hidden if cart is empty.'''
        c = Client()
        book = Book.objects.get(titre='Un paradigme')
        u = '/catalog/detail/%s' % book.pk
        response = c.get(u)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('remove', response.content.decode())

    def test_remove_button_hidden_in_page_detail_when_cart_not_empty_but_other_book_still_not_in_cart(self):
        '''Insure remove button is hidden if cart is not empty but the detail belongs to another book not in cart.'''
        c = Client()
        book = Book.objects.get(titre='Un paradigme')
        add_item_url = reverse('cart:add_item', kwargs={'pk': book.pk})
        c.post(add_item_url, follow=True)
        book2 = Book.objects.get(titre='Toujours mieux!')
        u = '/catalog/detail/%s' % book2.pk
        response = c.get(u)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('remove', response.content.decode())

    def test_checkout_page_exists(self):
        c = Client()
        check_url = '/cart/checkout/'
        response = c.get(check_url)
        self.assertEqual(response.status_code, 200)

    def test_valid_static_settings(self):
        result = finders.find('style.css')
        print(result)
        self.assertIsNotNone(result)
        c = Client()
        print(finders.searched_locations)
        response = c.get('/')
        #self.assertTemplateUsed(response,)
        self.assertEqual(200, response.status_code)
