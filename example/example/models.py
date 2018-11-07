from django.db import models
from django_countries.fields import CountryField
from django.db.models.deletion import CASCADE


class Author(models.Model):
    name = models.CharField(max_length=60)
    nationality = CountryField()


class Book(models.Model):
    name = models.CharField(max_length=60)
    description = models.TextField()
    author = models.ForeignKey(Author, on_delete=CASCADE)
    published_at = models.DateField(auto_now=True)

