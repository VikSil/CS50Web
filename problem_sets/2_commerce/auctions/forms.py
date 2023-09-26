from .models import *
from django.utils.translation import gettext_lazy as label
from django import forms


#form rendered for new auction page
class NewAuctionForm(forms.ModelForm):
    """
    Form for an Auction - includes all fields except Bid, which is a separate model
    """
    class Meta:
        model = Auction
        fields = ('UserID', 'title', 'description', 'imageURL', 'CategoryID')
        widgets = {
            'UserID' : forms.HiddenInput(attrs={}), #userID field is invisible
            'title' : forms.TextInput(attrs={'autocomplete': 'off', 'class':'form-control'}),
            'description' : forms.Textarea(attrs={'autocomplete': 'off', 'class':'form-control'}),
            'imageURL' : forms.URLInput(attrs={'autocomplete': 'off', 'class':'form-control'}),
            'CategoryID' : forms.Select(attrs={'class':'form-control'}), #allows selecion from Category model
          
        }
        labels = {
            'imageURL': label("Image"),
            'CategoryID': label("Category"),
        }
        

class NewBidForm(forms.ModelForm):
    """
    Form for a bid - both minimum bid and new bid field
    """    
    #pass in kwargs, depending on which view creates the form
    def __init__(self, *args, **kwargs):
        min = kwargs.pop("min", None) #minimum bid
        ext = kwargs.pop("extended",None) #extend field - used for formatting purposes on lisitng page
        temp_text = 'Input $' + str(min) + ' or more' #placeholder text
        super().__init__(*args, **kwargs)
        #both kwargs will be passed by get_listing view function
        if min and ext:
            self.fields["amount"].widget = forms.NumberInput(attrs={'placeholder': temp_text, 'autocomplete':'off', 'min':min, 'class':'form-control bid-field'})
        #only min will be passed by add_listing view function
        elif min:
            self.fields["amount"].widget = forms.NumberInput(attrs={'placeholder': temp_text, 'autocomplete':'off', 'min':min, 'step':0.01,  'class':'form-control'})


    class Meta:
        model = Bid
        fields = ('amount',)
        labels = {
             'amount': label(""),
        }
