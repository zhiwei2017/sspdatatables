from __future__ import unicode_literals
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sspdatatablesExample.settings')

import django
django.setup()


from example.models import Author, Book


if __name__ == "__main__":
    authors = [
        {"name": "a", "nationality": "DE"},
        {"name": "b", "nationality": "US"},
        {"name": "c", "nationality": "CN"},
        {"name": "d", "nationality": "GB"},
    ]
    books = [
        {"name": "1", "description": "111111111111111111111111111111111111111111111111111111111111111111111111111111111"},
        {"name": "2", "description": "222222222222222222222222222222222222222222222222222222222222222222222222222222222"},
        {"name": "3", "description": "333333333333333333333333333333333333333333333333333333333333333333333333333333333"},
        {"name": "4", "description": "444444444444444444444444444444444444444444444444444444444444444444444444444444444"},
    ]
    a_bulk, b_bulk = [], []
    for a in authors:
        a_bulk.append(Author(**a))
    Author.objects.bulk_create(a_bulk)

    a_ids = Author.objects.all().values_list('id', flat=True)
    for i in range(len(books)):
        b_bulk.append(Book(author_id=a_ids[i], **books[i]))
    Book.objects.bulk_create(b_bulk)