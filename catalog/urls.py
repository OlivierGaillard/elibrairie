from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from . import views


app_name = 'catalog'

urlpatterns = [
    url(r'^listall/$', views.BookListView.as_view(), name='listall'),
    url(r'^listcat/(?P<cat>[\w-]+)$', views.BookCategory.as_view(), name='listcat'),
    url(r'detail/(?P<pk>[0-9]+)$', views.BookDetailView.as_view(), name='detail'),
    ]