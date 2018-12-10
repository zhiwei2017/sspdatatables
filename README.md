## Introduction

### Background

In a Django project, a lot of tables are used to display the information stored
 in DB. However, with the time goes by, the DB grows bigger and bigger, such 
 that the table needs more time to load the content. In this case, reducing the 
 loading time becomes the most import task for software developers. 
 The common used way is using the server side processing table, which just loads
  a small part of the information at each time. 

To use the server side processing table, we have two options: either we develop 
a new one, or we just use the one implemented by someone else. For the first one,
 we have to invest a lot of time and energy, besides that we also make sure it 
 can be used anywhere. That's pretty difficult and less interesting for me 
 (thinking of the javascript code). For the second option, actually we just need
  to customize it. That's easy to achieve.

[datatables](https://datatables.net/) is a javascript package, which provides 
a lot of nice functions including the server side processing. However, using it 
in a Django project is not easy. To simplify its usage, I decided to implement 
a small package.

### Brief

**sspdatatables** is a python package for Django project. It uses the 
[datatables](https://datatables.net/) package and provides a nice 
Django-project-friendly interface for implementing the server side processing table.

Using this package you can implement not only a filterable, orderable and server
 side processing table. In common case, you don't even need to define the query 
 function, I already did it for you.

### Package Structure
```
sspdatatables
|   __init__.py
|   apps.py
|   datatables.py
|   forms.py
|
|---utils
|   |   __init__.py
|   |   decorator.py
|   |   enum.py
|   |   data_type_ensure.py
|
|---templates
|   |
|   |---datatables
|   |   |
|   |   |---html
|   |   |   table.html
|   |   |
|   |   |---js
|   |   |   footer.js
|   |   |   general.js
|   |
|---templatetags
    |   __init__.py
    |   form_field.py
|
|---tests
    |    __init__.py
    |    test_data_type_ensure_doctest.txt
    |    test_enum_doctest.txt
```


## How To Use

### Setup

1. run `pip install sspdatatables`
2. add `sspdatatables` in the `INSTALLED_APPS` in **settings.py**
3. add `sspdatatables/templates/` in the `DIRS` of `TEMPLATES` in **settings.py**

### Tutorial

In this section I will use an example project to explain how to use **sspdatatables**

Project **sspdatatablesExample**:

*structure*:
```
sspdatatablesExample
|   manage.py
|   manuals.py
|   requirements.txt
|
|---example
|   |   __init__.py
|   |   admin.py
|   |   apps.py
|   |   models.py
|   |   tests.py
|   |   urls.py
|   |   views.py
|   |
|   |---migrations
|   |   |   __init__.py
|   |   |   0001_initial.py
|   |
|   |---templates
|       |   index.html
|       |   overview.html
|
|---sspdatatablesExample
    |   __init__.py
    |   admin.py
    |   apps.py
    |   settings.py
    |   tests.py
    |   urls.py
    |   wsgi.py
    |
    |---migrations
        |   __init__.py
```

Content of **models.py** file in **example** app
```
from django.db import models
from django_countries.fields import CountryField


class Author(models.Model):
    name = models.CharField(max_length=60)
    nationality = CountryField()


class Book(models.Model):
    name = models.CharField(max_length=60)
    description = models.TextField()
    author = models.ForeignKey(Author, on_delete=None)
    published_at = models.DateField(auto_now=True)
```

We want to display the *name*, *published_at*, *author_name*,  
*author_nationality* information of books.

Our table should look like:

| Action | Name | Author | Author Nationality | Published At |
|------|----|------|------------------|------------|
| :pencil: | book a   | person 1 | country 1| Jul. 18, 2000|
| :pencil: | book b   | person 2 | country 2| Jul. 18, 1999|

> ##### Notice:
> * In datatables the column number is 0-index, which means the column *Action* is 
actually column **0**, column *Name* is column **1**

After having a picture of what we want, we can start to implement it.

#### Steps:
##### Step 1.
create a folder **datatables** in app **example** and add empty files:
**__init__.py**, **datatables.py**, **enums.py**, **forms.py**, **serializers.py** in it
> ###### Explaination:
> * **sspdatatables** requisite files are normally not used by other files, so 
putting them together helps you to keep your project's structure clear and 
simple (at least for the usage of **sspdatatables**).

##### Step 2.
in file **enums.py** input the following code:

```python
from sspdatatables.utils.enum import TripleEnum


class BookEnum(TripleEnum):
    ID = (1, "id", "id")
    NAME = (2, "name", "name__icontains")
    AUTHOR_NAME = (3, "author__name", "author__name__icontains")
    AUTHOR_NATIONALITY = (4, "author__nationality", "author__nationality")
    PUBLISHED_AT = (5, "published_at", "published_at")
```
> ###### Explaination:
> * First, we need to import the `TripleEnum` from `sspdatatables`. Then we 
create a subclass for it to define a mapping, which is a 3-element tuple, (that's 
why the enumeration class called `TripleEnum`).
> * The first element of the mapping means the **column number** in the table, 
the second element is the corresponding **field name** defined in the model class,
 and the third element is the **filter key** for the field.
> * The purpose of creating this enumeration class is that with knowing the 
column number we can use the corresponding **field name** to order the table's 
content and the corresponding **filter key** to filter the content.

##### Step 3.
in file **serializers.py** input the following code:

```python
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
    published_at = serializers.DateField(format='%b. %d, %Y', required=False)

    class Meta:
        model = Book
        fields = ('id', 'name', 'published_at', 'author')
```
> ##### Explaination:
> What we do here is actually defining the **ModelSerializer** for the table. 
There are two reasons for creating two ModelSerializers (one for Author and one for Book):
> 1. to access the foreign key referenced record's information, you have to 
define a **ModelSerializer** for it. That's defined by **Django REST framework**
> 2. we want to display not only the book's information but also its author's 
information, and the author is referenced as a foreign key in book
> ###### Notice:
> * If you use **CountryField** in your model class and you want to display the 
**country name** instead of the **country code** in the table, you have to use 
the same way as I defined for the **nationality** in the `AuthorSerializer` class
 (in the serialized data to get the country name, you can use `item.nationality.name`).
> * If you want to display the date in a specific format, you have to use the 
same name of this date field to declare a new `serializers.DateField` and specify the format 
(`serializers.DateField` corresponds to the `models.DateField` and `serializers.DateTimeField` corresponds to `models.DateTimeField`).

For more information about **Django REST framework**, you can visit [http://www.django-rest-framework.org/#tutorial](http://www.django-rest-framework.org/#tutorial)

##### Step 4.
in file **datatables.py** input the following code:

```python
from sspdatatables.datatables import DataTables
from .serializers import BookSerializer
from .enums import BookEnum
from .forms import BookFieldSelectForm


class BookDataTables(DataTables):

    class Meta:
        serializer = BookSerializer
        form = None
        structure = [
            {
                "id": "actions", "serializer_key": None,
                "header": "Actions", "searchable": False,
                "orderable": False, "footer_type": None,
            },
            {
                "id": "id", "serializer_key": 'id',
                "header": "ID", "searchable": True,
                "orderable": True, "footer_type": "input",
            },
            {
                "id": "name", "serializer_key": 'name',
                "header": "Name", "searchable": True,
                "orderable": True, "footer_type": "input",
            },
            {
                "id": "author", "serializer_key": 'author.name',
                "header": "Author", "searchable": True,
                "orderable": True, "footer_type": "input",
            },
            {
                "id": "author_nationality", "serializer_key": 'author.nationality.name',
                "header": "Author Nationality", "searchable": True,
                "orderable": True, "footer_type": "input",
            },
            {
                "id": "published_at", "serializer_key": 'published_at',
                "header": "Published At", "searchable": True,
                "orderable": True, "footer_type": "input",
                "placeholder": "YYYY-MM-DD",
            },
        ]
        col_triple_enum = BookEnum

```
> ###### Explaination:
> * The class `DataTables` works as a bridge to connect the display table and the DB:
>   * configures the table's frame according to its internal variable `structure`
>   * serializes the records from DB for displaying (variable `serializer`)
>   * applies the filter condition provided by the table to the DB with the help 
of its internal variable `col_triple_enum`
>   * customizes the table footer's search field to *select* field instead of the default *input* field (variable `form`)
> * The usage of `DataTables` is quite simple, you just need to create a subclass 
for it and define its internal Meta class's variables.
> * So far we just want to have a table with footer search field (in form of *input*). 
At last, I will show you how to change the footer search field to *select* type.
> ###### Notice:
> * If your table has a complicated query and you want to customize the query 
function, you can redefine the functions `_get_filter_dict`, `_get_order_key`, 
`_filtering`, `_slicing`, `filter_by_args` or `process` inside your defined 
subclass of `DataTables` as you need. In this case you need to read the source code first.

##### Step 5.
So far we already set up the backend part for using `sspdatatables`. In this step 
we start to deal with the frontend part.

Two views functions are needed: one is for rendering the table's frame, another 
one is for loading the table's content. 

Firstly, in file **view.py** of the app *example* create the first views function 
for displaying the tables' frame:

```python
from django.shortcuts import render
from django.http import JsonResponse
from .datatables import BookDataTables
from sspdatatables.utils.decorator import ensure_ajax
from collections import OrderedDict

def overview(request):
    book_datatables = BookDataTables()
    context = book_datatables.get_dt_elements()
    context.update({
        "title": "Books",
    })
    return render(request, 'overview.html', context)
```
> ###### Explaination:
> * through the function `get_dt_elements` you can get the frame (the return 
result of function `get_dt_elements` is a dictionary containing just one 
key-value pair), and you can also extend the `context` in case you want to 
render more variables

Secondly, still in this file create the second views function for loading the content:
```python
@ensure_ajax(['GET'])
def get_book_api(request):
    pre_search_condition = OrderedDict([('select_related', 'author')])
    book_datatables = BookDataTables()
    result = book_datatables.process(pre_search_condition=pre_search_condition,
                                      **request.GET)
    return JsonResponse(result)
```
> ###### Explaination:
> * through the decorator `ensure_ajax` we can make sure only the ajax request 
with allowed request method(s) is accepted by the views function. 
> * the `pre_search_condition` parameter of the function `process` must be an 
**OrderedDict** type:
    - The key in `pre_search_condition` is the function name in the *ModelManager* 
    of the model class 'Book', such as `selected_related`, `filter`, `values` etc. 
    - The value in in `pre_search_condition` is the corresponding function's parameters' 
    values. For example:
        + if you use `select_related` as the key, you can input a single value as 
        the related DB table or a list of values. 
        + if you use `filter` as the key, its value must be a dictionary, in 
        which a key-value pair means a *filter key* and its corresponding *filter value*, 
        such as `OrderedDict([('filter', {'name__icontains', 'Django'})])`
> * the `DataTables` class gonna iterate the `pre_search_condition` and apply 
those conditions by order.
> * since the `author` is a foreign key in `Book` model class, we need to set the 
`select_related` in `pre_search_condition`

Thirdly, define the urls for both views functions like:
```python
from django.conf.urls import url
from example.views import overview, get_book_api


urlpatterns = [
    url(r'^books/$', overview, name='book_overview'),
    url(r'^api/$', get_book_api, name='book_api'),
]
```

##### Step 6.
In this step we gonna write some *html* code and *javascript* code.

1. prepare a html file for the table, in `sspdatatablesExample` project I create
 a html file called `overview.html` in app `example`'s `templates` folder. 
 It looks like as following:
 
   ```html
    {% extends "index.html" %}
    
    {% load static %}
    
    {% block content %}
    {% endblock %}
    
    
    {% block scripts %}
    {% endblock %}
   ```

2. in the `block content` include the `'datatables/html/table.html` file from 
`sspdatatables`, and in the `block scripts` include `datatables/js/general.js` 
from `sspdatatables`.Now the `overview.html` should be like:

    ```html
    {% extends "index.html" %}
    
    {% load static %}
    
    {% block content %}
    <div class="row">
        <div class="col-md-12">
        {% include 'datatables/html/table.html' %}
        </div>
    </div>
    {% endblock %}
    
    
    {% block scripts %}
    {% include 'datatables/js/general.js' %}
    // using passed sspdatatables variable in context to replace the footer with input field or select field
    {% include 'datatables/js/footer.js' %}
    {% endblock %}
    ```

3. in the `block scripts` declare an instance of `DataTable` with the settings 
you want (here I will provide some common used settings). The `overview.html` becomes:

    ```html
    {% extends "index.html" %}
    
    {% load static %}
    
    {% block content %}
    <div class="row">
        <div class="col-md-12">
        {% include 'datatables/html/table.html' %}
        {% csrf_token %}
        </div>
    </div>
    {% endblock %}
    
    
    {% block scripts %}
    {% include 'datatables/js/general.html' %}
    // using passed sspdatatables variable in context to replace the footer with input field or select field
    {% include 'datatables/js/footer.js' %}
    
    <script>
    function render_actions(data, type, row) {
        var content = "";
        content += '<a class="btn btn-warning btn-xs" href="#" data-toggle="tooltip" title="Edit"><i class="fa fa-edit"></i></a>';
        return content;
    }
    
    /* here is the main function */
    $(document).ready(function() {
        // DataTable definition
        var table = $('#example').DataTable({
            "scrollY": "400px",
            "scrollX": true,
            "scrollCollapse": true,
            "order": [[ 1, "asc" ]],   // define the default _ordering column and _ordering format
            "processing": true,        // Enable or disable the display of a 'processing' indicator when the table is being processed
            "serverSide": true,        // important to use the server side processing
            "deferRender": true,       // read the documentation in datatables website
            "lengthMenu": [[10, 25, 50, 100], [10, 25, 50, 100]],    // length menu, read the documentation
            "paging": true,
            "pagingType": "full_numbers",
            "ajax": {
                "url": '{% url 'book_api' %}',
                "type": "POST",
                "headers": {
                    'X-CSRFToken': $('[name=csrfmiddlewaretoken]').val(),
                },
                "dataSrc":function (json) {
                    return json.data;
                },
                "data": function ( d ) {
                    return $.extend( {}, d, {
                        "total_cols": {{dt_structure|length}},
                    } );
                }
            },
            "columns": [
                // using django loop to define the stucture of the columns
                {% for item in dt_structure %}
                    {
                        "data": {% if item.serializer_key %}'{{item.serializer_key}}'{% else %} null {% endif %}, render: function (data, type, row) {
                            {% if item.id == 'actions' %}
                                return render_actions(data, type, row);
                            {% else %}
                                return data;
                            {% endif %}
                        },
                        "searchable": {% if item.searchable %} true {% else %} false {% endif %},
                        "orderable": {% if item.orderable %} true {% else %} false {% endif %},
                    },
                {% endfor %}
            ],
        });
        // hide the global filter and the footer, since in this view we don't need the footer
        $("#example_filter").hide();
    
        // single line without text wrapping
        $("#example").addClass("nowrap");
    
        // Apply the search
        apply_search(table);
    });
    </script>
    {% endblock %}
    ```

You can read the documentation in `DataTable` website to know about the javascript settings.

At this point, we already implement out table for the model class `Book`. If you 
want to know how to customize the footer search field, you can go the next step.

##### Step 7.
in the file `forms.py` in folder `datatables` of app `example` input the following code:

```python
from sspdatatables.forms import AbstractFooterForm
from django.forms import ChoiceField
from django_countries import countries


class BookFieldSelectForm(AbstractFooterForm):
    def get_author_nationality_choices(self):
        return [(None, 'Select')] + list(countries.countries.items())

    class Meta:
        fields = [("author_nationality", ChoiceField),]

```
> ###### Explaination:
> in `sspdatatables` there is a form class called `AbstractFooterForm`, which 
simplify the definition of the form class for the footer search field. What you need to do is
>    1. in the inside `Meta` class define the variable `fields` as a list of 2-element tuples: 
>        - first element is the **id** of the column (defined in the variable 
`structure` of class `BookDataTables` in `datatables.py` file)
>        - the second element is its corresponding footer field type (currently 
it just supports `ChoiceField`).; 
>    2. define a function for every element in `fields`. The name of the function
 must be `get_<first element in the tuple>_choices`. And this function return 
 the choices for this select field in form of list of tuples.

After that, there are only two small steps remaining, go to the `datatables.py` file
1. set the value of variable `form` of class `BookDataTables` to the form class 
we just defined `BookFieldSelectForm`
2. find the corresponding column's frame definition in variable `structure` of 
class `BookDataTables`, change the value of key `footer_type` to `'select'`

The `datatables.py` file should be:

```python
from sspdatatables.datatables import DataTables
from .serializers import BookSerializer
from .enums import BookEnum
from .forms import BookFieldSelectForm


class BookDataTables(DataTables):

    class Meta:
        serializer = BookSerializer
        form = BookFieldSelectForm
        structure = [
            {
                "id": "actions", "serializer_key": None,
                "header": "Actions", "searchable": False,
                "orderable": False, "footer_type": None,
            },
            {
                "id": "id", "serializer_key": 'id',
                "header": "ID", "searchable": True,
                "orderable": True, "footer_type": "input",
            },
            {
                "id": "name", "serializer_key": 'name',
                "header": "Name", "searchable": True,
                "orderable": True, "footer_type": "input",
            },
            {
                "id": "author", "serializer_key": 'author.name',
                "header": "Author", "searchable": True,
                "orderable": True, "footer_type": "input",
            },
            {
                "id": "author_nationality", "serializer_key": 'author.nationality.name',
                "header": "Author Nationality", "searchable": True,
                "orderable": True, "footer_type": "select",
            },
            {
                "id": "published_at", "serializer_key": 'published_at',
                "header": "Published At", "searchable": True,
                "orderable": True, "footer_type": "input",
                "placeholder": "YYYY-MM-DD",
            },
        ]
        col_triple_enum = BookEnum
```

Enjoy!

The source code of `sspdatatablesExample` is included in the package's *example* folder.
