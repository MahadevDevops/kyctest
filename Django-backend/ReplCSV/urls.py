from django.conf.urls import url
from django.urls import path

from . import views

urlpatterns = [
    url(r'^replinshments/$', views.CSVGenerate.as_view(),name='repl'),
]