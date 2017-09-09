from django.views.generic import ListView, DetailView
from catalog.models import Book, Category
from cart.cartutils import article_already_in_cart, get_cart_items


def add_categories_to_context(context):
    """
    Helper function to add the list of categories to the context.
    It is used in catalog.views and cart.CartView
    :param context: the context instance of the view
    :return: the context instance
    """
    categories = Category.objects.all()
    context['categories'] = categories
    return context

def add_total_books(context):
    total = Book.objects.count()
    context['total_books'] = total
    return context

# TODO: explain why this import must come after the def add_categories_to_context??
from cart.views import add_cart_counter_to_context

class BookListView(ListView):
    """
    This view return all books. Its name is 'listall'.
    """
    model = Book
    template_name = 'catalog/list.html'
    context_object_name = 'books'

    def get_context_data(self, **kwargs):
        ctx = super(BookListView, self).get_context_data(**kwargs)
        ctx = add_total_books(ctx)
        ctx = add_cart_counter_to_context(self.request, ctx)
        return add_categories_to_context(ctx)


class BookCategory(ListView):
    """
    This view return the books of one category. Its name is 'listcat'.
    """
    model = Book
    template_name = 'catalog/list.html'
    context_object_name = 'books'

    def get_queryset(self):
        cat_nom_param = self.kwargs['cat']
        cat = Category.objects.filter(nom=cat_nom_param).first()
        if cat:
            return cat.book_set.all()
        return Book.objects.all()

    def get_context_data(self, **kwargs):
        ctx = super(BookCategory, self).get_context_data(**kwargs)
        ctx = add_cart_counter_to_context(self.request, ctx)
        ctx = add_total_books(ctx)
        return add_categories_to_context(ctx)



class BookDetailView(DetailView):
    model = Book
    template_name = 'catalog/detail.html'
    context_object_name = 'book'


    def get_context_data(self, **kwargs):
        ctx = super(BookDetailView, self).get_context_data(**kwargs)
        ctx = add_cart_counter_to_context(self.request, ctx)
        ctx = add_total_books(ctx)
        cart_items = get_cart_items(self.request)
        ctx['book_in_cart'] = article_already_in_cart(cart_items, self.object)
        return add_categories_to_context(ctx)


