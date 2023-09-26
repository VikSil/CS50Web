from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Model for user information
    """
    password =  models.CharField(max_length=128, verbose_name="password")
    last_login = models.DateTimeField(blank=True, null=True, verbose_name="last login")
    is_superuser = models.BooleanField(default=False)
    username = models.CharField(error_messages={"unique": "A user with that username already exists."}, max_length=150, unique=True)
    first_name = models.CharField(blank=True, max_length=150)
    last_name = models.CharField(blank=True, max_length=150)
    email = models.EmailField(blank=True, max_length=254)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    groups = models.ManyToManyField(blank=True, related_name="user_set", related_query_name="user", to="auth.group")
    user_permissions = models.ManyToManyField(blank=True, related_name="user_set", related_query_name="user", to="auth.permission")

class Category(models.Model):
    """
    Model for auction category
    """
    name = models.CharField(max_length = 15, null=True)

    def __str__(self):
        return f"{self.name}"

class Auction(models.Model):
    """
    Model for auction - all fields except bid, which is a separate model 
    """
    UserID = models.ForeignKey(User, on_delete = models.PROTECT, related_name = "auction_author")
    title = models.CharField(max_length = 50, null=True)
    description = models.CharField(max_length = 200, null=True)
    imageURL = models.URLField(blank = True, null=True)
    CategoryID = models.ForeignKey(Category, on_delete= models.PROTECT, blank = True, null=True, related_name = "auction_category")
    active = models.BooleanField(default = True)
    watchers = models.ManyToManyField(User, blank = True, related_name = "auction_watchers")

    def __str__(self):
        return f"ID = {self.id}, {self.title}"

class Bid(models.Model):
    """
    Model for bid
    """
    UserID = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "bid_bidder")
    AuctionID = models.ForeignKey(Auction, on_delete = models.CASCADE, default = 0, related_name = "bid_auction")
    when = models.DateTimeField(auto_now_add=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    IsStarting = models.BooleanField(default = True)

    def __str__(self):
        #Render string representation differently depending on whether this is a starting bid/minimum price
        if {self.IsStarting}:
            return f"ID = {self.id}, Strating price of {self.amount} by {self.UserID} on listing '{self.AuctionID.title}'"
        else:
            return f"ID = {self.id}, Bid of {self.amount} by {self.UserID} on listing '{self.AuctionID.title}'"

class Comment(models.Model):
    """
    Model for comment
    """
    UserID = models.ForeignKey(User, on_delete = models.SET_NULL, blank = True, null=True, related_name = "comment_author")
    AuctionID = models.ForeignKey(Auction, on_delete = models.CASCADE, default = 0, related_name = "comment_auction")
    when = models.DateTimeField(auto_now_add=True, blank=True)
    text = models.CharField(max_length = 200, null=True)

    # looks ugly, but gives out all the data
    def __str__(self):
        return f"ID = {self.id}, UserID = {self.UserID}, AuctionID = {self.AuctionID}, when = {self.when}, text = {self.text}"

