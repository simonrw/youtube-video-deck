from django import forms


class SearchForm(forms.Form):
    term = forms.CharField(
        label="Term",
        max_length=100,
        widget=forms.TextInput(attrs={"class": "bg-gray-300 rounded-lg py-2"}),
    )
