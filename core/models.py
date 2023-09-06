from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
# Create your models here.
class Profile(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    image=models.ImageField(upload_to="profile_photos", default="default-profile.jpg")
    bio=models.TextField(blank=True)
    location=models.CharField(max_length=200, blank=True)
    def __str__(self):
        return self.user.username

class Test(models.Model):
    name=models.CharField(max_length=200)
    age=models.IntegerField()
    def __str__(self):
        return self.name

class Post(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    image=models.ImageField(upload_to="posts")
    caption=models.TextField(blank=True)
    created=models.DateTimeField(auto_now_add=True)
    likes=models.IntegerField(default=0)

    def __str__(self):
        return self.user.username

class Likepost(models.Model):
    post=models.ForeignKey(Post,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    created=models.DateTimeField(default=datetime.now)
    def __str__(self):
        return self.user.username

class Comment(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    post=models.ForeignKey(Post,on_delete=models.CASCADE)
    comment=models.TextField()
    created=models.DateTimeField(default=datetime.now)
    def __str__(self):
        return self.user.username

class Follow(models.Model):
    follower=models.ForeignKey(User,on_delete=models.CASCADE, related_name="follower")
    followed=models.ForeignKey(User,on_delete=models.CASCADE, related_name="followed")
    def __str__(self):
        return self.follower.username+ "  follows "+self.followed.username