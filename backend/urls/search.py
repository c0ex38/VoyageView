from django.urls import path
from backend.home.search import SearchUserAPI

urlpatterns = [
    path('', SearchUserAPI.as_view(), name='search'),
]
