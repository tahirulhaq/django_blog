from calendar import c
from cgitb import html
from enum import Flag
from turtle import pos
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .models import Post, Comment, Reply
from .forms import PostForm, UserRegisterForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from .tokens import account_activation_token
from django.core.mail import EmailMessage
from django.contrib.sessions.models import Session

# Create your views here.
global my_dict
my_dict = {}


def registerUser(request):
    form = UserRegisterForm()
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            current_site = get_current_site(request)
            mail_subject = 'Activation link has been sent to your email id'
            message = render_to_string('blog/acc_active_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user),
            })
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            return HttpResponse('Please confirm your email address to complete the registration')
        else:
            HttpResponse('An error occured during registration')
    return render(request, 'blog/login_register.html', {'form': form})


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    page = 'login'
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            HttpResponse('User does not exist')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            HttpResponse('Username OR password does not exist')
    context = {'page': page}
    return render(request, 'blog/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def home(request):
    if not request.session.exists(request.session.session_key):
        request.session.create()
    posts = Post.objects.all()
    context = {'posts': posts}
    return render(request, 'blog/home.html', context)


def createPost(request):
    form = PostForm()
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            form.save()
        return redirect('home')

    context = {'form': form}
    return render(request, 'blog/post_form.html', context)


def updatePost(request, pk):
    post = Post.objects.get(id=pk)
    form = PostForm(instance=post)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'blog/post_form.html', context)


def deletePost(request, pk):
    post = Post.objects.get(id=pk)
    if request.method == 'POST':
        post.delete()
        return redirect('home')
    return render(request, 'blog/delete.html', {'obj': post})


def deleteComment(request, pk):
    comment = Comment.objects.get(id=pk)

    if request.user != comment.user:
        return HttpResponse('You are not allowed here')
    if request.method == 'POST':
        comment.delete()
        return redirect('home')
    return render(request, 'blog/delete.html', {'obj': comment})


def post_details(request, slug):

    global my_dict
    post = Post.objects.get(slug=slug)
    comments = post.comment_set.all()
    replies = Reply.objects.all()

    if post.id in my_dict and my_dict[post.id] != request.session.session_key:
        my_dict = {}

    if post.id in my_dict:
        is_liked = True
    else:
        is_liked = False

    if request.method == 'POST':
        comment = Comment.objects.create(
            user=request.user,
            post=post,
            body=request.POST.get('body')
        )
        return redirect('post', slug=post.slug)

    context = {'post': post, 'post_comments': comments, 'replies': replies,
               'is_liked': is_liked, 'total_likes': post.total_likes()}
    return render(request, 'blog/post_detail.html', context)


# solution for error => request.is_ajax is not a function
def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def like_post(request):
    global my_dict
    post = get_object_or_404(Post, id=request.POST.get('id'))

    if post.id in my_dict and my_dict[post.id] != request.session.session_key:
        my_dict = {}

    if post.id in my_dict:
        print('decrement likes')
        post.decrement_likes()
        my_dict.pop(post.id)
    else:
        print('increment likes')
        post.increment_likes()
        my_dict[post.id] = request.session.session_key

    if post.id in my_dict:
        is_liked = True
    else:
        is_liked = False

    context = {'post': post, 'is_liked': is_liked,
               'total_likes': post.total_likes()}
    if is_ajax(request):
        html = render_to_string('blog/like_section.html',
                                context, request=request)
        return JsonResponse({'form': html})


def ReplyPage(request, id, slug):
    post = Post.objects.get(slug=slug)
    comment = Comment.objects.get(id=id)
    if request.method == 'POST':
        reply = Reply.objects.create(
            comment=comment,
            description=request.POST.get('description')
        )
    return redirect('post', slug=post.slug)


def deleteReply(request, id, slug):
    reply = Reply.objects.get(id=id)
    post = Post.objects.get(slug=slug)
    if request.method == 'POST':
        reply.delete()
        return redirect('post', slug=post.slug)
    return render(request, 'blog/delete.html', {'obj': reply})


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return HttpResponse('Thank you for your email confirmation. Now you can login your account.<a href="http://127.0.0.1:8000/">Go to Home</a>')
    else:
        return HttpResponse('Activation link is invalid!')


# def post_details(request, pk):
#     post = Post.objects.get(id=pk)
#     comments = post.comments.filter(parent__isnull=True)
#     if request.method == 'POST':
#         # comment has been added
#         comment_form = CommentForm(data=request.POST)
#         if comment_form.is_valid():
#             parent_obj = None
#             # get parent comment id from hidden input
#             try:
#                 # id integer e.g. 15
#                 parent_id = int(request.POST.get('parent_id'))
#             except:
#                 parent_id = None
#             # if parent_id has been submitted get parent_obj id
#             if parent_id:
#                 parent_obj = Comment.objects.get(id=parent_id)
#                 # if parent object exist
#                 if parent_obj:
#                     # create reply comment object
#                     reply_comment = comment_form.save(commit=False)
#                     # assign parent_obj to reply comment
#                     reply_comment.parent = parent_obj
#             # normal comment
#             # create comment object but do not save to database
#             new_comment = comment_form.save(commit=False)
#             # assign ship to the comment
#             new_comment.post = post
#             # save
#             new_comment.save()
#             return HttpResponseRedirect(post.get_absolute_url())
#     else:
#         comment_form = CommentForm()

#     context = {'post': post, 'post_comments': comments}
#     return render(request, 'blog/post_detail.html', context)

  # post = Post.objects.get(id=pk)
    # post_comments = post.comment_set.all()
    # comments = post.comments.filter(parent__isnull=True)

    # if request.method == 'POST':
    #     comment = Comment.objects.create(
    #         user=request.user,
    #         post=post,
    #         body=request.POST.get('body')
    #     )
    #     return redirect('post', pk=post.id)

    # context = {'post': post, 'post_comments': comments}
    # return render(request, 'blog/post_detail.html', context)
