from pickle import TRUE
from django.contrib.auth.models import AbstractUser
from django.db import models
from numpy import ones_like


class User(AbstractUser):
    pass

class Listing(models.Model):
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="creator")
    item = models.CharField(max_length=64)
    price = models.FloatField()
    description = models.CharField(max_length=64)
    datetime = models.DateTimeField()
    picture = models.ImageField(blank=True, null=True, upload_to='auctions/images/listings')
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.item}"


class Bid(models.Model):
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="item_on_bid")
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bidder")
    price = models.FloatField()

    class Meta:
        unique_together = (('item', 'bidder'),)

    def __str__(self):
        return f"{self.bidder} bidded {self.price} for {self.item}"


class Watchlist(models.Model):
    item = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="item_on_watch")
    watcher = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watcher")

    class Meta:
        unique_together = (('item', 'watcher'),)

    def __str__(self):
        return f"{self.watcher} watching for {self.item}"


class Comment(models.Model):
    publisher = models.ForeignKey(User, on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE)
    message = models.CharField(max_length=64)

    class Meta:
        unique_together = (('publisher', 'message'),)

    def __str__(self):
        return f"{self.publisher} commented on {self.listing}"