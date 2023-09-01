from markdown2 import Markdown
from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse
from . import util

#class to rended for entry input and edit form
class NewEntryForm(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs = {'placeholder': "Input Page Title Here"}), label = "")
    desc = forms.CharField(widget=forms.Textarea(attrs = {'placeholder': "Input Content Here"}), label = "")
    pageedit = forms.BooleanField(widget = forms.HiddenInput(), initial=False, required=False)



def index(request):
    """
    Returns a list of all entries
    """
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries(),
        "title": "All Pages" #the same template will be used for search results, hence pass title
    })

def page_exists(pagename):
    """
    Checks if an entry exists
    """
    if util.get_entry(pagename) is None:
        return False
    return True

def get_page(request,pagename):
    """
    Returns the page that the user has requested or 404 page
    if entry is not found
    """
    #if the user calls page that does not exist - return 404
    if not page_exists(pagename):
        return render(request, "encyclopedia/404.html",{
        })
    #if page exists - return rendered markdown entry
    else:
        markdowner = Markdown()
        return render(request, "encyclopedia/entrypage.html",{
            "entry" : markdowner.convert(util.get_entry(pagename)),
            "pagename" : pagename 
    })

def add_page(request):
    """
    Returns the input form for adding new page to the encyclopedia
    """
    #POST the new entry - is triggered when user hits "Save" button on the new entry page
    if request.method == "POST":
        addedpage = NewEntryForm(request.POST)
        #if valid input - create a new .md file
        if addedpage.is_valid():
            #check if the page with that title already exists
            addtitle = addedpage.cleaned_data["title"]
            editpage = addedpage.cleaned_data["pageedit"]
            #if page with that title already exists and user is not editing it - re-render this with warning
            if page_exists(addtitle) and not editpage:
                return render(request, "encyclopedia/addpage.html", {
                "addpageform":addedpage,
                "error" : "This entry already exists",
                "pagename" : "Add New Entry "
                })
            #if new entry or user editing existing entry - save it
            else:
                adddesc = addedpage.cleaned_data["desc"]
                util.save_entry(addtitle.title(), adddesc)
                return get_page(request, addtitle.title())
        #if input not valid - throw the error back at the user
        else:
            return render(request, "encyclopedia/addpage.html", {
                "addpageform":addedpage,
                "error" : "Input is not valid",
                "pagename" : "Add New Entry "
            })

    #GET the new entry page
    return render(request, "encyclopedia/addpage.html", {
        "addpageform": NewEntryForm,
        "pagename" : "Add New Entry "
    })

def edit_entry(request): 
    """
    Accepts input to edit an existing page and saves the changes
    """
    #if user called edit url manually 
    if request.method == "GET":
        return  render(request, "encyclopedia/404.html",{
        })
    
    # if POST - user clicked 'Edit butotn on an existing entry'
    else:
        editpage = NewEntryForm(request.POST)
        return render (request, "encyclopedia/addpage.html", {
                "addpageform":editpage,
                "pagename" : "Edit Entry "
                })
        

def random_page(request):
    """
    Returns a random page that exists on the encyclopedia
    """
    return get_page(request, util.get_random_entry())


def find_page(request):
    """
    Returns search results
    """
    if request.method == "POST":
        pagetofind =request.POST["q"]
        #if page exists with the exact search term as a title - retrun that page
        if page_exists(pagetofind):
            return get_page(request, pagetofind)
        # if no exact title exists - look for entries where keyword is substring to the title
        else:
            entries = util.find_entry(pagetofind)
            #if any of the entries have the keyword as a substring - return list of entries
            if len(entries) > 0:
                return render(request, "encyclopedia/index.html", {
                    "entries": entries,
                    "title": "Search Results" # same templeate is used for homepage, hence pass title
                })
            #if the keyword does not exist as a substring amongst the entries - return 404
            else:
                return render(request, "encyclopedia/404.html",{
                        })