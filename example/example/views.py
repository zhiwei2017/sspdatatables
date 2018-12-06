from django.shortcuts import render
from .datatables import BookDataTables
from sspdatatables.utils.decorator import ensure_ajax, dt_json_response
from collections import OrderedDict


def overview(request):
    book_datatables = BookDataTables()
    context = book_datatables.get_table_frame()
    context.update({
        "title": "Books",
    })
    return render(request, 'overview.html', context)


@ensure_ajax(['POST'])
def get_book_api(request):
    pre_search_condition = OrderedDict([('select_related', 'author')])
    book_datatables = BookDataTables()
    result = book_datatables.process(pre_search_condition=pre_search_condition,
                                     **request.POST)
    return dt_json_response(result)
