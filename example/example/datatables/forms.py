from sspdatatables.forms import AbstractFilterForm
from django.forms import ChoiceField
from django_countries import countries


class BookFieldSelectForm(AbstractFilterForm):
    def get_author_nationality_choices(self):
        return [(None, 'Select')] + list(countries.countries.items())

    class Meta:
        fields = [("author_nationality", ChoiceField),]
