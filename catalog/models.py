from django.db import models
from django.shortcuts import reverse
# Create your models here.

class Category(models.Model):
    nom = models.CharField('Catégorie', max_length=50)
    slug = models.SlugField(max_length=50, unique=True)
    description = models.TextField()

    class Meta:
        verbose_name_plural = 'Catégories'

    def __str__(self):
        return self.nom


class Book(models.Model):
    titre  = models.CharField( max_length=200, null=True)
    auteur = models.CharField(max_length=100, null=True)
    categories = models.ManyToManyField(Category)
    prix   = models.DecimalField(max_digits=9, decimal_places=2, null=True)
    quantite = models.IntegerField(null=True)
    description = models.TextField(default='')
    photo = models.ImageField(upload_to='covers', blank=True, null=True)

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse('books:detail', kwargs={'pk' : self.pk})
