"""Posts views configuration"""

from django.contrib.auth.decorators import login_required
from django.core.handlers.wsgi import WSGIRequest
from django.core.paginator import Paginator
from django.db.models import Count
from django.db.models.query import QuerySet
from django.shortcuts import render, get_object_or_404, redirect


from .forms import PostForm, CommentForm
from .models import Post, Group, User, Follow
from .settings import POSTS_PER_PAGE


def get_paginator_page(request: WSGIRequest, object_list: QuerySet,
                       per_page: int = POSTS_PER_PAGE) -> Paginator:
    return Paginator(object_list, per_page).get_page(request.GET.get('page'))


def index(request):
    return render(request, 'posts/index.html', {
        'page_obj': get_paginator_page(
            request,
            Post.objects.select_related('author').select_related('group')
        ),
    })


def group_posts(request, slug):
    group = get_object_or_404(
        Group.objects.prefetch_related('posts__author'),
        slug=slug
    )
    return render(request, 'posts/group_list.html', {
        'group': group,
        'page_obj': get_paginator_page(request, group.posts.all()),
    })


def profile(request, username):
    author = get_object_or_404(
        User.objects.annotate(posts_count=Count('posts')).prefetch_related(
            'posts__group'),
        username=username
    )
    following = False
    if request.user.is_authenticated:
        following = Follow.objects.filter(
                user=request.user,
                author__username=username
            ).exists()
    return render(request, 'posts/profile.html', {
        'author': author,
        'page_obj': get_paginator_page(request, author.posts.all()),
        'following': following
    })


def post_detail(request, post_id):
    post = get_object_or_404(
        Post.objects.select_related('author').annotate(posts_count=Count(
            'author__posts')).select_related('group').prefetch_related(
            'comments'),
        pk=post_id
    )
    return render(request, 'posts/post_detail.html', {
        'post': post,
        'form': CommentForm()
    })


@login_required
def post_create(request):
    form = PostForm(request.POST or None, files=request.FILES or None)
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    nw_pst = form.save(commit=False)
    nw_pst.author = request.user
    nw_pst.save()
    return redirect('posts:profile', request.user.username)


@login_required
def post_edit(request, post_id):
    query_post = Post.objects.select_related('author').select_related('group')
    post = get_object_or_404(query_post, pk=post_id)
    if post.author != request.user:
        return redirect('posts:profile', request.user.username)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if not form.is_valid():
        context = {'form': form, 'is_edit': True}
        return render(request, 'posts/create_post.html', context)
    form.save()
    return redirect('posts:post_detail', post_id)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post.objects.select_related('author'), pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    return render(request, 'posts/follow.html', {
        'page_obj': get_paginator_page(
            request,
            Post.objects.select_related('author').select_related(
                'group').filter(author__following__user=request.user)
        ),
    })


@login_required
def profile_follow(request, username):
    following = Follow.objects.filter(
        user=request.user,
        author__username=username
    ).exists()
    author = get_object_or_404(User, username=username)
    if not (following or request.user == author):
        Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.filter(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)
