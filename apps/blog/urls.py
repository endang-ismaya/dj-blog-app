from django.urls import path


from apps.blog import views



urlpatterns = [
    path("", views.index, name="blog__index"),
]
