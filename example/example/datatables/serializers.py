from example.models import Book, Author
from rest_framework import serializers
from django_countries.serializers import CountryFieldMixin
from django_countries.serializer_fields import CountryField


class AuthorSerializer(CountryFieldMixin, serializers.ModelSerializer):
    nationality = CountryField(country_dict=True)

    class Meta:
        model = Author
        fields = ('name', 'nationality')


class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    published_at = serializers.DateField(format='%b. %d, %Y',
                                         required=False)

    class Meta:
        model = Book
        fields = ('id', 'name', 'published_at', 'author')
