from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView

from apps.blog.models import Post


def post_list(request):
    """blog index view"""
    posts = Post.published.all()

    # pagination with 5 posts per page
    paginator = Paginator(posts, 5)
    page_number = request.GET.get("page", 1)
    posts = paginator.get_page(page_number)

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


class PostListView(ListView):
    """blog list view"""

    queryset = Post.published.all()
    context_object_name = "posts"
    paginate_by = 5
    template_name = "blog/post/list.html"
