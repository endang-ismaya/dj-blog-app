import markdown
from django.contrib.syndication.views import Feed
from django.template.defaultfilters import truncatewords_html
from django.urls import reverse_lazy

from apps.blog.models import Post


class LatestPostFeed(Feed):
    title = "My Blog"
    link = reverse_lazy("blog:post_list")
    description = "New posts of my awesome blog)"

    def items(self):
        return Post.published.all()[:5]

    def item_title(self, item: Post):
        return item.title

    def item_description(self, item: Post):
        return truncatewords_html(markdown.markdown(item.body), 50)

    def item_pubdate(self, item: Post):
        return item.publish_at
