from django.urls import path


from apps.blog import views


urlpatterns = [
    path("", views.post_list, name="blog__post_list"),
    path("<int:id>/", views.post_detail, name="blog__post_detail"),
]
