from django.conf.urls import url
from example.views import overview, get_book_api


urlpatterns = [
    url(r'^books/$', overview, name='book_overview'),
    url(r'^api/$', get_book_api, name='book_api'),
]