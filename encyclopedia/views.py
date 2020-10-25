from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django import forms

from . import util
from wiki import context_processors

import random

# create form class for the page name
class NewPageNameForm(forms.Form):
    attrs = {'style':"margin:10px;"}
    name = forms.CharField(label="Page Name", widget=forms.TextInput(attrs=attrs))

# create form class for the page content 
class NewPageForm(forms.Form):
    page = forms.CharField(label="Page Markdown Content")
    def __init__(self, *args, **kwargs):  # allows pre existing value to be added in
        self.value = kwargs.pop('value', None)
        super().__init__(*args, **kwargs)
        attrs = {'style': "width:100%; height: 300px;"}
        self.fields['page'].initial = self.value
        self.fields['page'].widget = forms.Textarea(attrs=attrs)


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def page(request, page_name):
    entry = util.get_entry(str(page_name))
    if entry == None:  # if the entry does not match an existing page
        return render(request, "encyclopedia/error.html", {
            "message": "Error. No such page exists. Try again."
            })
    else: 
        entry = util.to_html(entry)  # convert from markdown to html
        return render(request, "encyclopedia/entry.html", {
            "entry": entry, "page_name": page_name,
            })
            
def random_page(request):
    entry_list = util.list_entries()
    random_entry = entry_list[random.randint(0, len(entry_list)-1)]  # gets random page
    return HttpResponseRedirect(reverse("wiki:page", args = [random_entry]))
    
def new_page(request):
    if request.method == "GET":  # renders a blank form for the user to input new page content
        return render(request, "encyclopedia/new_page.html", {
            "page_form": NewPageForm(),
            "page_name_form": NewPageNameForm()
            })
    else:  # if request.method is 'POST', retreives form data, cleans it, and saves the page content
        form_name = NewPageNameForm(request.POST)
        if form_name.is_valid():
            name = form_name.cleaned_data["name"]
        else:
            return render(request, "encyclopedia/new_page.html", {
                "form": NewPageNameForm(value=form_name)
            })
        if util.get_entry(name):
            return render(request, "encyclopedia/error.html", {
                "message": "Error. A page with that name already exists."
            })
        form_content = NewPageForm(request.POST)
        if form_content.is_valid():
            page = form_content.cleaned_data["page"]
        else:
            return render(request, "encyclopedia/new_page.html", {
                "form": NewPageForm(value=form_content)
            })
        util.save_entry(name, page)
        return HttpResponseRedirect(reverse("wiki:page", args = [name]))
        
def search_results(request):
    if request.method == "GET":
        return render(request, "encyclopedia/error.html", {
            'message':'Error. You have to search something before you can access this page.'
        })
    else:
        q = context_processors.SearchForm(request.POST)  # gets form from context_processors.py
        if q.is_valid():
            q = q.cleaned_data["q"]
        else:
            return render(request, "encyclopedia/error.html", {
                'message':'Error. Invalid data. Try to search again.'
            })
        list_of_matched_entries = []
        capitalized_search = q.upper()  # makes it not case sensitive
        for entry in util.list_entries():  # loops through the entries to check if the search query matched or was in the entry name
            capitalized_entry = entry.title()
            if capitalized_entry == q.title():  # if search query directly matches page name, go to that page
                return HttpResponseRedirect(reverse("wiki:page", args = [q]))
                break
            elif capitalized_search in entry.upper():  # otherwise, return a list of the entries that partially match
                list_of_matched_entries.append(entry)
        if not list_of_matched_entries:
            return render(request, "encyclopedia/error.html", {
                'message': "Error: Your search came up with no results."
            })
        return render(request, "encyclopedia/search_results.html", {
            'entries':list_of_matched_entries
        })
        
def edit_page(request, pagename):
    entry = util.get_entry(str(pagename))
    if request.method == "GET":  # renders a form with the pre existing markdown content for the chosen page
        return render(request, "encyclopedia/edit_page.html", {
                "page_form": NewPageForm(value=entry),
                "page_name": pagename
            })
    else:  # if request.method is 'POST', saves new form content and redirects to the chosen page
        form_content = NewPageForm(request.POST)
        if form_content.is_valid():
            page = form_content.cleaned_data["page"]
        else:
            return render(request, "encyclopedia/edit_page.html", {
                "form": NewPageNameForm(value=form_content)
            })
        util.save_entry(pagename, page)
        return HttpResponseRedirect(reverse("wiki:page", args = [pagename]))
        