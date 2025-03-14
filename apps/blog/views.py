from django.http import Http404
from django.shortcuts import get_object_or_404, render
from apps.blog.models import Post


def post_list(request):
    """blog index view"""
    posts = Post.published.all()
    context = {"posts": posts}
    return render(request, "blog/post/list.html", context)


def post_detail(request, year, month, day, post):
    """blog detail view"""
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post,
        publish_at__year=year,
        publish_at__month=month,
        publish_at__day=day,
    )

    context = {"post": post}
    return render(request, "blog/post/detail.html", context)
