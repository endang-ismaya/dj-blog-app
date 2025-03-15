from django.conf import settings
from django.contrib.postgres.search import SearchQuery, SearchRank, SearchVector
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.db.models import Count
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_POST
from django.views.generic import ListView
from taggit.models import Tag

from apps.blog.forms import CommentForm, EmailPostForm, SearchForm
from apps.blog.models import Post


def post_list(request, tag_slug=None):
    """blog index view"""
    posts = Post.published.all()
    tag = None

    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts = posts.filter(tags__in=[tag])

    # pagination with 5 posts per page
    paginator = Paginator(posts, 5)
    page_number = request.GET.get("page", 1)
    posts = paginator.get_page(page_number)

    context = {"posts": posts, "tag": tag}
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
    # list of active comments for this post
    comments = post.comments.filter(active=True)
    # form for users to comment
    form = CommentForm()
    # list of similar posts
    post_tags_ids = post.tags.values_list("id", flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count("tags")).order_by(
        "-same_tags", "-publish_at"
    )[:4]

    context = {
        "post": post,
        "comments": comments,
        "form": form,
        "similar_posts": similar_posts,
    }
    return render(request, "blog/post/detail.html", context)


class PostListView(ListView):
    """blog list view"""

    queryset = Post.published.all()
    context_object_name = "posts"
    paginate_by = 5
    template_name = "blog/post/list.html"


def post_share(request, post_id):
    """blog share view"""
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent_flag = False
    if request.method == "POST":
        # form was submitted
        form = EmailPostForm(request.POST)
        if form.is_valid():
            # form fields passed validation
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cd['name']} ({cd['email']}) recommends you read {post.title}"
            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}'s comments: {cd['comments']}"
            )
            # ... send email
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [cd["to"].strip()]
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=from_email,
                    recipient_list=to_email,
                    fail_silently=False,
                )
                sent_flag = True
            except Exception as e:
                print(f"Error sending mail: {e}")
                form.add_error(None, "An error occured while sending the email.")
            sent_flag = True
    else:
        form = EmailPostForm()

    context = {"post": post, "form": form, "send_flag": sent_flag}
    return render(request, "blog/post/share.html", context)


@require_POST
def post_comment(request, post_id):
    """blog comment view"""
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED,
    )
    comment = None
    # A comment was posted
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Create a Comment object without saving it to the database
        comment = form.save(commit=False)
        # Assign the post to the comment
        comment.post = post
        # Save the comment to the database
        comment.save()

    return render(
        request,
        "blog/post/comment.html",
        {"post": post, "form": form, "comment": comment},
    )


def post_search(request):
    """blog search view"""
    form = SearchForm()
    query = None
    results = []

    if "query" in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data["query"]
            search_vector = SearchVector("title", "body")
            search_query = SearchQuery(query)
            results = (
                Post.published.annotate(
                    search=search_vector, rank=SearchRank(search_vector, search_query)
                )
                .filter(search=search_query)
                .order_by("-rank")
            )

    return render(
        request,
        "blog/post/search.html",
        {"form": form, "query": query, "results": results},
    )
