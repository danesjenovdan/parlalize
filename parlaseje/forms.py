from dal import autocomplete
from django import forms
from .models import Legislation

class LegislationForm(forms.ModelForm):
    """Form for posts."""

    class Meta:
        model = Legislation
        fields = ('text', 'status', 'result', 'note', 'abstractVisible', 'is_exposed', 'icon', 'mdt_fk', 'epa', 'extra_note')
        widgets = {
            'mdt_fk': autocomplete.ModelSelect2(url='wb-autocomplete'),
        }

    def __init__(self, *args, **kwargs):
        super(LegislationForm, self).__init__(*args, **kwargs)
        #  add_related_field_wrapper(self, 'post')

    def save(self, *args, **kwargs):
        instance = super(LegislationForm, self).save(commit=False)
        return instance