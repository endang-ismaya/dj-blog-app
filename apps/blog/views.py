from django.shortcuts import render

# Create your views here.

def index(request):
    """blog index view"""
    context = {}
    return render(request, "blog/index.html", context)
