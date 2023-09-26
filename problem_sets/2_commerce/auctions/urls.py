from django.urls import path

from . import views

app_name = "auctions"
urlpatterns = [
    path("", views.index, name="index"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("add/", views.add_listing, name="add"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("categories/", views.categories, name="categories"),
    
    path("shortlist=<int:CategoryID>/", views.shortlist, name="shortlist"),
    path("listing=<int:AuctionID>", views.get_listing, name = "listing")
]
