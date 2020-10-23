from django import forms

class SearchForm(forms.Form):
    q = forms.CharField(label='', widget=forms.TextInput(attrs={'placeholder': 'Search Encyclopedia'}))

def layout_form(request):
    return {
        "search_form": SearchForm()
    }