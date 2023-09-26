from .forms import NewBidForm
from .models import Bid, Comment

def save_bid (bid_to_save: NewBidForm, user_id: Bid.UserID, auction_id: Bid.AuctionID, starting: bool) -> None:
    """
    Saves a new bid input from listing page into the Bid model
    """
    new_bid = Bid()
    new_bid.UserID = user_id
    new_bid.AuctionID = auction_id
    new_bid.amount = bid_to_save.cleaned_data['amount']
    new_bid.IsStarting = starting
    new_bid.save()

def save_comment(text: str, user_id: Comment.UserID, auction_id: Comment.AuctionID) -> None:
    """
    Saves a new comment input from listing page into the Comment model
    """
    new_comment = Comment()
    new_comment.UserID = user_id
    new_comment.AuctionID = auction_id
    new_comment.text = text
    new_comment.save()

