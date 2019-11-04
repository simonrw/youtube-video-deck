from django import forms


class SearchForm(forms.Form):
    term = forms.CharField(label="Term", max_length=100)
