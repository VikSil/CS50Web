from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class Post(models.Model):
    """
    Model for post data
    """

    UserID = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="post_author"
    )
    message = models.CharField(max_length=150, null=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    likedby = models.ManyToManyField(User, blank=True, related_name="post_fans")

    def get_likes(self):
        return "\n".join([u.username for u in self.likedby.all()])


class Following(models.Model):
    """
    Links between User model rows to keep track of who follows whom
    """

    CreatorID = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_followed"
    )
    FollowerID = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_following"
    )
