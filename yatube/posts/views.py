from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from yatube.settings import PAGE_CONST

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User


def index(request):
    post_list = Post.objects.all()
    paginator = Paginator(post_list, PAGE_CONST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_list = Post.objects.filter(group=group)
    paginator = Paginator(posts_list, PAGE_CONST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    if (
        request.user.is_authenticated
        and author != request.user
        and Follow.objects.filter(author=author, user=request.user).exists()
    ):
        following = True
    elif author == request.user:
        following = None
    else:
        following = False
    posts_list = Post.objects.filter(author=author)
    paginator = Paginator(posts_list, PAGE_CONST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
        'author': author,
        'posts': posts_list,
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    author = post.author
    posts_list = Post.objects.filter(author=author)
    count = posts_list.count()
    if request.method == 'POST':
        form = CommentForm(
            request.COMMENT or None
        )
        if form.is_valid():
            comments = form.save(commit=False)
            comments.save
            return redirect('posts:post_detail', post.id)
        else:
            return render(request, 'posts/post_detail.html', {'form': form})
    else:
        form = CommentForm()
        comment = Comment.objects.filter(post=post)
        context = {
            'post': post,
            'count': count,
            'form': form,
            'comments': comment,
        }
        return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    groups = Group.objects.all()
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:profile', post.author.username)
        else:
            return render(request, 'posts/create_post.html', {'form': form})
    else:
        form = PostForm()
        is_edit = False
        context = {
            'form': form,
            'groups': groups,
            'is_edit': is_edit,
        }
        return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    groups = Group.objects.all()
    if request.method == 'POST':
        form = PostForm(
            request.POST or None,
            files=request.FILES or None,
            instance=post
        )
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect('posts:post_detail', post.id)
    else:
        form = PostForm(instance=post)
        is_edit = True
        context = {
            'form': form,
            'groups': groups,
            'post': post,
            'is_edit': is_edit,
        }
        return render(request, 'posts/create_post.html', context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    user = request.user
    authors = user.follower.all().values('author')
    post_list = Post.objects.filter(author__in=authors)
    paginator = Paginator(post_list, PAGE_CONST)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if (request.user == author
            or Follow.objects.filter(user=request.user, author=author,).exists()):
        return redirect('posts:profile', username=username)
    else:
        Follow.objects.create(
            user=request.user,
            author=author,
        )
        return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.get(
        user=request.user,
        author=author,
    )
    follow.delete()
    return redirect('posts:profile', username=username)
