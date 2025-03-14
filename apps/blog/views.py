from django.http import Http404
from django.shortcuts import render
from apps.blog.models import Post


def post_list(request):
    """blog index view"""
    posts = Post.published.all()
    context = {"posts": posts}
    return render(request, "blog/post/list.html", context)


def post_detail(request, id):
    """blog detail view"""
    try:
        post = Post.published.get(id=id)
    except Post.DoesNotExist:
        raise Http404("No Post found")

    context = {"post": post}
    return render(request, "blog/post/detail.html", context)
