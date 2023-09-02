from django.urls import path

from . import views

app_name = "encyclopedia"
urlpatterns = [
    path("", views.index, name="index"),
    path("addpage/", views.add_page, name="addpage"),
    path("randompage/", views.random_page, name="randompage"),
    path("searchresults/", views.find_page, name="findpage"),
    path("edit/", views.edit_entry, name="editentry"),
    # this needs to be at the very bottom, otherwise it will intercept other requests
    path("<str:pagename>/", views.get_page, name="getpage"),
]
