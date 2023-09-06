from django.shortcuts import render
from .serializers import *
from .models import *
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.http import JsonResponse
from django.contrib.auth.models import User
import jwt,datetime
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta
# Create your views here.
def formt_created(created):
    now = timezone.now()

    # Calculate the time difference
    time_difference = now - created

    if time_difference < timedelta(minutes=1):
        return "now"
    elif time_difference < timedelta(hours=1):
        minutes = int(time_difference.total_seconds() / 60)
        return f"{minutes} {'minute' if minutes == 1 else 'minutes'} ago"
    elif time_difference < timedelta(days=1):
        hours = int(time_difference.total_seconds() / 3600)
        return f"{hours} {'hour' if hours == 1 else 'hours'} ago"
    elif time_difference < timedelta(days=30):
        days = time_difference.days
        return f"{days} {'day' if days == 1 else 'days'} ago"
    else:
        months = int(time_difference.days / 30)
        return f"{months} {'month' if months == 1 else 'months'} ago"


@api_view(['GET','POST'])
def tests(request):
    if request.method == "GET":
        tests=Test.objects.all()
        serializer=TestSerializer(tests,many=True)
        return Response(serializer.data)
    if request.method == "POST":
        serializer=TestSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"success":"data added"})

@api_view(['GET','PUT','DELETE'])
def test(request,id):
    test=Test.objects.filter(id=id).first()
    if request.method == "GET":
        if test:
            serializer=TestSerializer(test)
            return Response(serializer.data)
        else:
            return Response({"error":"data not found"})
    if request.method == "PUT":
        serializer=TestSerializer(test,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
    if request.method == "DELETE":
        test.delete()
        return Response({"success":"deleted"})

@api_view(['POST'])
def signup(request):
    if request.method == "POST":
        email=request.data.get("email")
        username=request.data.get("username")
        password=request.data.get("password")
        check_user=User.objects.filter(username=username).first()
        if check_user:
            return Response({"error":"username is taken"})
        else:
            serializer=UserSerializer(data=request.data)
            if serializer.is_valid():
                new_user=User.objects.create_user(email=email,password=password,username=username)
                new_user.save()
                profile=Profile.objects.create(user=new_user)
                profile.save()
                return Response({"success":"user created"})
            else:
                return Response({"error":"invalid data"})

@api_view(['POST','PUT','DELETE'])              
def user(request,id):
    user=User.objects.filter(id=id).first()
    token=request.data.get("token")
    payload=jwt.decode(token,"secret",algorithms=["HS256"])
    logged_user=User.objects.get(id=payload["id"])
    if request.method == "POST":
        if user:
            profile=Profile.objects.get(user=user)
            _posts=Post.objects.filter(user=user)
            posts=[]
            for post in _posts:
                posts.append({
                    "id":post.id,
                    "image":"http://127.0.0.1:8000/"+post.image.url
                })

            is_following=""
            follow_exist=Follow.objects.filter(followed=user,follower=logged_user).first()
            if follow_exist:
                is_following="Yes"
            else:
                is_following="No"
            profile={
                "id":user.id,
                "username":user.username,
                "email":user.email,
                "image":"http://127.0.0.1:8000/"+profile.image.url,
                "bio":profile.bio,
                "is_following":is_following
            }
            _followers=Follow.objects.filter(followed=user)
            _following=Follow.objects.filter(follower=user)
            followers=len(_followers)
            following=len(_following)
            context={
                "profile":profile,
                "logged_user":logged_user.username,
                "posts":posts,
                "followers":followers,
                "following":following,
            }
            return Response(context)
           
        else:
            return Response({"error":"user not found"})
    if request.user == "PUT":
        pass
    if request.method == "DELETE":
        user.delete()
        return Response({"success":"user deleted"})


@api_view(['POST'])
def login(request):
    if request.method == "POST":
        username=request.data.get("username")
        password=request.data.get("password")
        user=User.objects.filter(username=username).first()
        if user:
            if user.check_password(password):
                payload={
                    "id":user.id,
                    "exp":datetime.datetime.utcnow()+datetime.timedelta(minutes=60),
                    "iat":datetime.datetime.utcnow()
                }
                token=jwt.encode(payload,"secret",algorithm="HS256")
                response=Response()
                response.set_cookie(key="jwt",value=token, httponly=True,samesite="None", secure=True)
                response.data={
                    "jwt":token
                }
                return response
            else:
                return Response({"password_error":"password  is incorrect"}) 
        else:
            return Response({"username_error":"user doesnt exist"})

@api_view(['POST'])
def home(request):
    if request.method == "POST":
        token=request.data.get("token")
        payload=jwt.decode(token,"secret",algorithms=["HS256"])
        user=User.objects.get(id=payload['id'])
        _profile=Profile.objects.get(user=user)
        profile={
            "id":user.id,
            "username":user.username,
            "email":user.email,
            "image":request.build_absolute_uri(_profile.image.url)
        }
        following=[]
        following_ids=[]
        _following=Follow.objects.filter(follower=user)
        _posts=Post.objects.order_by("-created")
        posts=[]
        for following in _following:
            following_ids.append(following.followed.id)
        
        for post in _posts:
            if post.user.id in following_ids or post.user == user:
                _profile=Profile.objects.get(user=post.user)
                likes=""
                if(post.likes == 0):
                    likes= "No likes"
                elif(post.likes == 1):
                    likes= "1 like"
                else:
                    likes = str(post.likes) + " likes"
                is_liked=""
                liked=Likepost.objects.filter(user=user,post=post).first()
                if liked:
                    is_liked="yes"
                else:
                    is_liked="No"

                posts.append({
                    "id":post.id,
                    "likes":likes,
                    "liked": is_liked,
                    "user_id":post.user.id,
                    "user":post.user.username,
                    "post_image": "http://127.0.0.1:8000/" + post.image.url,
                    "caption":post.caption,
                    "created":formt_created(post.created),
                    "profile_image":request.build_absolute_uri(_profile.image.url)
                })
        
        _users=User.objects.exclude(username="admin")
        users=_users[:5]
        suggestions=[]
        for _user in users:
            if _user.id not in following_ids and _user.id != user.id:
                _profile=Profile.objects.get(user=_user)
                suggestions.append({
                    "id":_user.id,
                    "username":_user.username,
                    "image":request.build_absolute_uri(_profile.image.url)
                })

        context={
            "profile":profile,
            "posts":posts,
            "suggestions":suggestions,
        }
        return Response(context)

@api_view(['POST','PUT'])
def settings(request):
    if request.method == "POST":
        token=request.data.get("token")
        payload=jwt.decode(token,"secret",algorithms=["HS256"])
        user=User.objects.get(id=payload['id'])
        serializer=UserSerializer(user)
        _profile=Profile.objects.get(user=user)
        profile={
            "location":_profile.location,
            "bio":_profile.bio,
            "image":request.build_absolute_uri(_profile.image.url)
        }
        context={
            "profile":profile,
            "user": serializer.data
        }
        return Response(context)
    if request.method == "PUT":
        token =request.data.get("token")
        payload=jwt.decode(token,"secret",algorithms=["HS256"])
        user=User.objects.get(id=payload['id'])
        profile=Profile.objects.get(user=user)
        username=request.data.get("username")
        email=request.data.get("email")

        if request.data.get("image"):
            image=request.data.get("image")
            location=request.data.get("location")
            bio=request.data.get("bio")
            profile.image=image
            profile.location=location
            profile.bio=bio
            profile.save()
        else:
            location=request.data.get("location")
            bio=request.data.get("bio")
            profile.location=location
            profile.bio=bio
            profile.save()

        check_user=User.objects.filter(username=username).first()
        if check_user:
            if check_user.username == user.username:
                user.email=email
                user.username=username
                user.save()
                serializer=UserSerializer(user)
                profile={
                    "image":request.build_absolute_uri(profile.image.url),
                    "location":profile.location,
                    "bio":profile.bio
                }
                context={
                    "success":"updated successfully",
                    "user":serializer.data,
                    "profile":profile
                }
                return Response(context)
            else:
                return Response({"error":"user exists"})
        else:
            user.email=email
            user.username=username
            user.save()
            serializer=UserSerializer(user)
            profile={
                "image": request.build_absolute_uri(profile.image.url),
                "location":profile.location,
                "bio":profile.bio
            }
            context={
                "success":"updated successfully",
                "user":serializer.data,
                "profile": profile
            }
            return Response(context)

@api_view(['PUT'])
def password(request):
    if request.method == "PUT":
        oldpassword=request.data.get("oldpasswd")
        newpassword=request.data.get("newpasswd")
        confpassword=request.data.get("confpasswd")
        token =request.data.get("token")
        payload=jwt.decode(token,"secret",algorithms=["HS256"])
        user=User.objects.get(id=payload['id'])
        if user.check_password(oldpassword):
            if newpassword != confpassword:
                return Response({"error":"confirmed password doesnt match the new password"})
            else:
                new_password=make_password(newpassword)
                user.password=new_password
                user.save()
                return Response({"success":"password updated successfully"})
        else:
            return Response({"error":"old password is invalid"})
        return Response({"msg":"hello"})

@api_view(['GET','POST'])
def posts(request):
    token=request.data.get("token")
    payload=jwt.decode(token,"secret",algorithms=["HS256"])
    user=User.objects.get(id=payload["id"])
    if request.method=="GET":
        posts=Post.objects.all()
        serializer=PostSerializer(posts,many=True)
        return Response(serializer.data)
    if request.method == "POST":
        caption=request.data.get("caption")
        image=request.data.get("image")
        post=Post.objects.create(user=user,image=image,caption=caption)
        post.save()
        return Response({"success":"post created"})


@api_view(["POST"])
def likepost(request):
    if request.method == "POST":
        id=request.data.get("id")
        token=request.data.get("token")
        payload=jwt.decode(token,"secret",algorithms=["HS256"])
        user=User.objects.get(id=payload["id"])
        post=Post.objects.get(id=id)
        like_exist=Likepost.objects.filter(user=user,post=post).first()
        if like_exist:
            like_exist.delete()
            post.likes-=1
            post.save()
            return Response({"success":"unliked post"})
        else:
            new_like=Likepost.objects.create(user=user,post=post)
            new_like.save()
            post.likes+=1
            post.save()
            return Response({"success":"liked post"})

@api_view(['GET'])            
def likes(request,id):
    if request.method == "GET":
        post=Post.objects.get(id=id)
        likes=Likepost.objects.filter(post=post)
        profiles=[]
        for like in likes:
            user=User.objects.get(username=like.user.username)
            profile=Profile.objects.get(user=user)
            profiles.append({
                "username":user.username,
                "image": request.build_absolute_uri(profile.image.url)
            })
        return Response(profiles)

@api_view(['GET','POST'])
def comments(request,id):
    post=Post.objects.get(id=id)
    if request.method == "GET":
        _comments=Comment.objects.filter(post=post)
        comments=[]
        for comment in _comments:
            profile=Profile.objects.get(user=comment.user)
            comments.append({
                "id":comment.id,
                "user":profile.user.username,
                "image":request.build_absolute_uri(profile.image.url),
                "comment":comment.comment,
                "created":comment.created
            })
        # serializer=CommentSerializer(comments, many=True)
        return Response(comments)
    if request.method == "POST":
        token=request.data.get("token")
        payload=jwt.decode(token,"secret",algorithms=["HS256"])
        user=User.objects.get(id=payload["id"])
        comment=request.data.get("comment")
        new_comment=Comment.objects.create(user=user,post=post,comment=comment)
        new_comment.save()
        return Response({"success" : "comment added"})

@api_view(["POST"])
def follow(request, id):
    if request.method == "POST":
        token=request.data.get("token")
        payload=jwt.decode(token,"secret",algorithms=["HS256"])
        follower=User.objects.get(id=payload["id"])
        followed=User.objects.get(id=id)
        follow_exist=Follow.objects.filter(followed=followed,follower=follower).first()
        if follow_exist:
            follow_exist.delete()
            return Response({"success":"unfollowed successfully"})
        else:
            new_follow=Follow.objects.create(follower=follower,followed=followed)
            new_follow.save()
            return Response({"success": "new follow added"})
@api_view(["GET"])
def followers(request,id):
    if request.method == "GET":
        # token=request.data.get("token")
        # payload=jwt.decode(token,"secret",algorithms=["HS256"])
        # logged_user=User.objects.get(id=payload["id"])
        user=User.objects.get(username=id)
        followers=[]
        _followers=Follow.objects.filter(followed=user)
        for follower in _followers:
            _user=User.objects.get(id=follower.follower.id)
            profile=Profile.objects.get(user=_user)
            followers.append({
                "id":_user.id,
                "username":_user.username,
                "image":request.build_absolute_uri(profile.image.url),
            })
        return Response(followers)

@api_view(["GET"])
def following(request,id):
    if request.method == "GET":
        user=User.objects.get(username=id)
        followings=[]
        _following=Follow.objects.filter(follower=user)
        for following in _following:
            _user=User.objects.get(id=following.followed.id)
            profile=Profile.objects.get(user=_user)
            followings.append({
                "id":_user.id,
                "username":_user.username,
                "image":request.build_absolute_uri(profile.image.url),
            })
        return Response(followings)
