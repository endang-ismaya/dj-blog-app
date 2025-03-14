from django.conf import settings
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, render
from django.views.generic import ListView

from apps.blog.forms import EmailPostForm
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
