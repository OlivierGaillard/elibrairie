from django.views.generic import TemplateView
from catalog.views import add_categories_to_context, add_total_books
from cart.views import add_cart_counter_to_context

def toto():
    return 'toto'

class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        ctx = super(IndexView, self).get_context_data(**kwargs)
        ctx = add_categories_to_context(ctx)
        ctx = add_cart_counter_to_context(self.request, ctx)
        ctx = add_total_books(ctx)
        return ctx

class TodoView(TemplateView):
    template_name = 'todo.html'

    def get_context_data(self, **kwargs):
        ctx = super(TodoView, self).get_context_data(**kwargs)
        ctx = add_categories_to_context(ctx)
        ctx = add_cart_counter_to_context(self.request, ctx)
        return ctx
