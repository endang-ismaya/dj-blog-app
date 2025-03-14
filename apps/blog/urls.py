from django.urls import path

from apps.blog import views

urlpatterns = [
    path("", views.post_list, name="blog__post_list"),
    path(
        "<int:year>/<int:month>/<int:day>/<slug:post>/",
        views.post_detail,
        name="blog__post_detail",
    ),
    path("posts/", views.PostListView.as_view(), name="blog__post_list_view"),
    path("<int:post_id>/share/", views.post_share, name="blog__post_share"),
]
