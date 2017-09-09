from django.db import models
from catalog.models import Book

class CartItem(models.Model):
    cart_id    = models.CharField(max_length=50)
    date_added = models.DateTimeField(auto_now_add=True)
    quantity   = models.IntegerField(default=1)
    book       = models.ForeignKey(Book, unique=False)

    class Meta:
        db_table = 'cart_items'
        ordering = ['date_added']

    def total(self):
        return self.quantity * self.book.prix

    @property
    def nom(self):
        return self.book.titre

    def prix(self):
        return self.book.prix

    def get_absolute_url(self):
        return self.book.get_absolute_url()

    def augment_quantity(self, quantity):
        self.quantity = self.quantity + int(quantity)
        self.save()

    def get_total_of_cart(session_id):
        """
        Select the cart_items for this session_id and sum the total
        of each item.
        :return: the total of cart content
        """
        cart_items = CartItem.objects.filter(cart_id=session_id)
        cart_total_list = [cart_item.total() for cart_item in cart_items]
        return sum(cart_total_list)
