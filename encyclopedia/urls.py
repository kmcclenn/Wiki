from django.urls import path

from . import views

app_name = "wiki"
urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:page_name>", views.page, name="page"),
    path("random_page", views.random_page, name="random_page"),
    path("new_page", views.new_page, name="new_page"),
    path("search_results", views.search_results, name="search_results"),
    path("edit_page/<str:pagename>", views.edit_page, name="edit_page")
]
