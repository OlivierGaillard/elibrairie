from django.test import TestCase, Client
from django.shortcuts import reverse
from .views import BookListView
from catalog.models import Category
import logging

# Create your tests here.
class TestCatalog(TestCase):

    fixtures = ['category.json', 'books.json']

    def setUp(self):
        pass

    def test_load_json(self):
        self.assertTrue(len(Category.objects.all()) > 0)
        cat_names = [cat.nom for cat in Category.objects.all()]

    def test_trie_categories(self):
        c = Client()
        logger = logging.getLogger('django')
        request_url = reverse('catalog:listcat', kwargs={'cat': 'psychologie'})
        self.assertEqual('/catalog/listcat/psychologie', request_url)
        response = c.get(reverse('catalog:listcat', kwargs={'cat': 'psychologie'}))
        self.assertEqual(response.status_code, 200)
        msg = "Livre 'Thérapie de la confiance en soi' pas trouvé dans la réponse."
        self.assertIn('confiance', response.content.decode(), msg)



