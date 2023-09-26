from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.db.models.aggregates import Max

from decimal import Decimal
import sys

from .models import *
from .utils import *
from .forms import *


def index(request):
    """
    Diaplays all of the active listings
    """
    listings = Auction.objects.filter(active = True).annotate(max_bid = Max("bid_auction__amount"))
    return render(request, "auctions/index.html", {
            #from Auction model, filter for active listings only and annotate (upend) to each max_bid
            # max_bid is a field in another model (Bid) that is linked to Auction by reverse_name  = bid_auction
            # and from that model we take __amount field and pick the maximum value
            "listings": listings,
            "title" : "Active Listings"
        }
    )

def add_listing(request):
    """
    Displays form to add a new listing
    """
    #POST user submits new auction information
    if request.method == "POST":  
        auction_form = NewAuctionForm(request.POST, request.FILES, prefix = "auction")
        bid_form = NewBidForm(request.POST, request.FILES, prefix = "bid")

        #if both auction and bid values are valid, save and return user to active listings list
        if auction_form.is_valid() and bid_form.is_valid():
            new_auction = auction_form.save()
            save_bid (bid_form, auction_form.cleaned_data["UserID"], new_auction, True)
            return HttpResponseRedirect(reverse("auctions:index"))

    #GET the new auction input page
    auction_form =  NewAuctionForm(prefix = "auction")
    #set the userID field default value to the current user - since the field is invisible, but needs a value
    auction_form.fields["UserID"].initial = User.objects.get(id = request.user.id)
    #set the categoryID field default value to None, since the field is optional 
    auction_form.fields["CategoryID"].initial = None
    #set the minimum starting bid to 0.01
    bid_form = NewBidForm(min = "0.01", prefix = "bid")
    bid_form.fields["amount"].label = "Starting Bid:"
    return render(request, "auctions/add_listing.html", {
        "newauctionform" : auction_form,
        "newbidform" : bid_form
    })

def watchlist(request):
    """
    Displays the watchlist
    """
    u = User.objects.get(id = request.user.id) #get the user id
    return render(request, "auctions/index.html", { #render the same page as All listings page
            #but only include the listings that the user is watching
            "listings":Auction.objects.filter(watchers = u).annotate(max_bid = Max("bid_auction__amount")),
            #and change the title of the page
            "title" : "Your Watchlist"
        }
    )

def shortlist(request, CategoryID):
    """
    Displays all auctions in a certain category
    """
    if CategoryID == 0: #if user pressed "All Categories" button, then send them to active listings page
        return HttpResponseRedirect(reverse("auctions:index"))
    else:     
        cat_name = Category.objects.filter(pk = CategoryID).first().name
        return render(request, "auctions/index.html", { #else get the subset of active listings in category and display them in active listings page
                "listings":Auction.objects.filter(active = True, CategoryID = CategoryID).annotate(max_bid = Max("bid_auction__amount")),
                "title" : "Active listings in category: " + cat_name #change the title of the page to include category name
            }
        )

def get_listing(request, AuctionID):
    """
    Displays selected listing
    """
    this_listing = Auction.objects.get(id = AuctionID)
    #pass differnet data depending on wheather the user is logged in or not
    if not (request.user.is_anonymous):
        watcher = this_listing.watchers.filter(pk = request.user.id)
        this_user = User.objects.get(id = request.user.id)
    else:
        watcher = None
        this_user =None

    #POST something - user submitted comment or bid, closed, watched/unwatched a listings
    if request.method == "POST": 
        #bid submitted
        if "bid-sub" in request.POST:
            bid_form = NewBidForm(request.POST, request.FILES, prefix = "bid")
            if bid_form.is_valid():
                save_bid (bid_form, this_user, this_listing, False)
                # add the listing to watchlist when user bids on it
                if not watcher:
                     this_listing.watchers.add(this_user)
                     watcher = this_listing.watchers.filter(pk = request.user.id) 

        #comment submitted
        if "comment-sub" in request.POST:
            save_comment(request.POST["comment-field"], this_user, this_listing) 

        #user clicked Watch/Unwatch button
        if "watch-sub" in request.POST: 
            if request.POST["watch-sub"] == "Watch":
                #add watcher to the database
                this_listing.watchers.add(this_user)
                watcher = this_listing.watchers.filter(pk = request.user.id)
            else:
                #delete watcher from the database
                if watcher:
                    this_listing.watchers.remove(request.user.id)
                    watcher = None    

        #user closed their own listing
        if "close-sub" in request.POST:
            this_listing.active = False    
            this_listing.save()       


    #GET a single listing - also returned after saving the POST request

    #get all Bids for the Auction, order by amount and pick the latest
    #validation to ensure that latest is also the highest is handled on POST
    max_bid = Bid.objects.all().filter(AuctionID = this_listing).order_by("when").last()
    if max_bid.IsStarting: #if no bids yet - allow input of the minimum bid amount
        min_bid = max_bid.amount
    else: #if ther eare previous bids on the listing, allow to increment bid by 1   
        min_bid = max_bid.amount + Decimal(1)
    winner = max_bid.UserID #displayed if the listing is closed
    bid_form = NewBidForm(min = min_bid, extended=True, prefix = "bid")
    comments = Comment.objects.all().filter(AuctionID = this_listing)

    #determines the text and function of Watch/Unwatch buton
    if watcher:
        watching = True
    else:
        watching = False
    
    return render(request, "auctions/listing.html",{
        "listing" : this_listing,
        "max_bid" : max_bid,
        "min_bid" : min_bid,
        "bidform" : bid_form,
        "comments" : comments,
        "watching" : watching,
        "winner" : winner
    })


def categories(request):
    """
    Displays categories page
    """
    return render(request, "auctions/categories.html", {
            "categories":Category.objects.all(),
        }
    )


#----------------------------------------------------------------------------------------------------------------------------------------
#----------------------------------------------------------------------------------------------------------------------------------------

def login_view(request):
    """
    Displays login page
    """
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("auctions:index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    """
    Logs user out
    """
    logout(request)
    return HttpResponseRedirect(reverse("auctions:index"))


def register(request):
    """
    Displays registration page
    """
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("auctions:index"))
    else:
        return render(request, "auctions/register.html")