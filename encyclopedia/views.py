from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect
from django import forms

from . import util
from wiki import context_processors

import random

class NewPageNameForm(forms.Form):
    attrs = {'style':"margin:10px;"}
    name = forms.CharField(label="Page Name", widget=forms.TextInput(attrs=attrs))

        
  

class NewPageForm(forms.Form):
    page = forms.CharField(label="Page Markdown Content")
    def __init__(self, *args, **kwargs):
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
    if entry == None:
        return render(request, "encyclopedia/error.html", {
            "message": "Error. No such page exists. Try Again."
            })
    else: 
        entry = util.to_html(entry) #convert from markdown to html
        return render(request, "encyclopedia/entry.html", {
            "entry": entry.items(), "page_name": page_name
            })
            
def random_page(request):
    entry_list = util.list_entries()
    random_entry = entry_list[random.randint(0, len(entry_list)-1)]
    return HttpResponseRedirect(reverse("wiki:page", args = [random_entry]))
    
def new_page(request):
    if request.method == "GET":
        return render(request, "encyclopedia/new_page.html", {
            "page_form": NewPageForm(),
            "page_name_form": NewPageNameForm()
            })
    else:
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
        q = context_processors.SearchForm(request.POST)
        if q.is_valid():
            q = q.cleaned_data["q"]
        else:
            return render(request, "encyclopedia/error.html", {
                'message':'Error. Invalid data. Try to search again.'
            })
        list_of_matched_entries = []
        for entry in util.list_entries():
            capitalized_search = q.upper()
            capitalized_entry = entry.title()
            if capitalized_entry == q.title():
                return HttpResponseRedirect(reverse("wiki:page", args = [q]))
                break
            elif capitalized_search in entry.upper():
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
    if request.method == "GET":
        return render(request, "encyclopedia/edit_page.html", {
                "page_form": NewPageForm(value=entry),
                "page_name": pagename    #NewPageNameForm(placeholder=pagename)
            })
    else:
        """
        form_name = NewPageNameForm(request.POST)
        if form_name.is_valid():
            name = form_name.cleaned_data["name"]
        else:
            return render(request, "encyclopedia/edit_page.html", {
                "form": NewPageNameForm(placeholder=form_name)
            })
        if util.get_entry(name) and name != pagename:
            return render(request, "encyclopedia/error.html", {
                "message": "Error. A page with that name already exists."
            })
        """
        form_content = NewPageForm(request.POST)
        if form_content.is_valid():
            page = form_content.cleaned_data["page"]
        else:
            return render(request, "encyclopedia/edit_page.html", {
                "form": NewPageNameForm(value=form_content)
            })
        util.save_entry(pagename, page)
        return HttpResponseRedirect(reverse("wiki:page", args = [pagename]))
        