from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.urls import reverse
from django.db.models import Max

from .models import User, Listing, Bid, Watchlist, Comment

 
def index(request):
    return render(request, "auctions/index.html", {
        "active": Listing.objects.filter(available=True),
        "inactive": Listing.objects.filter(available=False)
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
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
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

def create(request):
    if request.method == "POST":
        creator = User.objects.get(pk=request.POST["creator"])
        title = request.POST["Title"]
        description = request.POST["Description"]
        price = request.POST["Price"]
        dt = request.POST["DateTime"]
        img = request.FILES["img"]
        listing = Listing(item=title, price=price, description=description, datetime=dt, picture=img, creator=creator)
        listing.save()
        return HttpResponseRedirect(reverse('index'))
    return render(request, "auctions/create.html")


def listing(request, listing_id):
    if request.method == "POST":
        user = User.objects.get(pk=request.POST["user"])
        listing = Listing.objects.get(pk=listing_id)
        form_id = request.POST["form_id"]

        # For adding to watchlist
        if form_id == '3':
            watching = Watchlist(item=listing, watcher=user)
            watching.save()

        # For deleting from watchlist
        if form_id == '4':
            watching = Watchlist.objects.filter(item=listing).get(watcher=user)
            watching.delete()

        # For commenting
        if form_id == '2':
            message = Comment(publisher=user, listing=listing, message=request.POST["messagebox"])
            message.save()
            
        # For bidding or closing
        if form_id == '1':
            if user != listing.creator:
                amount = request.POST["bid_amt"]

                # Django decides insert or update
                if not Bid.objects.filter(item=listing).filter(bidder=user).exists():
                    bid = Bid(item=listing, bidder=user, price=amount)
                else: 
                    bid = Bid.objects.filter(item=listing).get(bidder=user)
                    bid.price = amount
                bid.save()
            else:
                listing.available = False
                listing.save()
        return HttpResponseRedirect(reverse('listing', args=(listing_id,)))

    # Checking bid
    listing = Listing.objects.get(pk=listing_id)
    bids = Bid.objects.filter(item=listing)
    if bids.exists():
        num_bids = bids.count()
        max_bid = bids.aggregate(Max('price'))['price__max']  # Aggregate max returns {'price_max': value} AND + 0.01 for higher bid
        winner = bids.get(price=max_bid).bidder  # Get returns object
    else:
        num_bids = 0
        max_bid = listing.price
        winner = listing.creator

    # Checking watchlist
    watchers = []
    for watched_item in Watchlist.objects.filter(item=listing):
        watchers.append(watched_item.watcher)

    if listing is not None:
        return render(request, 'auctions/listing.html', {
            'listing': listing,
            'num_bids': num_bids,
            'max_bid': max_bid,
            'winner': winner,
            'comments': Comment.objects.filter(listing=listing),
            'watched': watchers
        })
    else:
        return Http404('Listing does not exist')

def watchlist(request, username):
    user = User.objects.get(username=username)
    listings = []
    for watched_item in Watchlist.objects.filter(watcher=user):
        listings.append(watched_item.item)

    return render(request, "auctions/watchlist.html", {
        "listings": listings,
    })
