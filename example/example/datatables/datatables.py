from sspdatatables.datatables import DataTables
from sspdatatables.constants import SearchArea
from .serializers import BookSerializer
from .enums import BookEnum
from .forms import BookFieldSelectForm


class BookDataTables(DataTables):

    class Meta:
        serializer = BookSerializer
        form = BookFieldSelectForm
        frame = [
            {
                "id": "actions", "serializer_key": None,
                "header": "Actions", "searchable": False,
                "orderable": False, "filter_type": None,
            },
            {
                "id": "id", "serializer_key": 'id',
                "header": "ID", "searchable": True,
                "orderable": True, "filter_type": "input",
            },
            {
                "id": "name", "serializer_key": 'name',
                "header": "Name", "searchable": True,
                "orderable": True, "filter_type": "input",
            },
            {
                "id": "author", "serializer_key": 'author.name',
                "header": "Author", "searchable": True,
                "orderable": True, "filter_type": "input",
            },
            {
                "id": "author_nationality", "serializer_key": 'author.nationality.name',
                "header": "Author Nationality", "searchable": True,
                "orderable": True, "filter_type": "select",
            },
            {
                "id": "published_at", "serializer_key": 'published_at',
                "header": "Published At", "searchable": True,
                "orderable": True, "filter_type": "input",
                "placeholder": "YYYY-MM-DD",
            },
        ]
        mapping = BookEnum
        search_area = SearchArea.Header
