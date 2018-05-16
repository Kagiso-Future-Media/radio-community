"""django_reddit URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.home_page, name='frontpage'),
    url(r'^comments/(?P<thread_id>[0-9]+)$', views.comments, name='thread'),
    url(r'^comments/submit/(?P<object_id>[0-9]+)/delete/$',
        views.delete_submission,
        name='delete_submission_comments'
        ),
    url(r'submit/(?P<object_id>[0-9]+)/report/$',
        views.report_submission,
        name='report_submission'
        ),
    url(r'submit/(?P<object_id>[0-9]+)/promote/$',
        views.promote_submission,
        name='promote_submission'
        ),
    url(r'^comments/comments/node/(?P<object_id>[0-9]+)/delete/$',
        views.delete_comment,
        name='delete_comment'
        ),
    url(r'^submit/$', views.submit, name='submit'),
    url(r'submit/(?P<object_id>[0-9]+)/delete/$',
        views.delete_submission,
        name='delete_submission'
        ),
    url(r'^post/comment/$', views.post_comment, name='post_comment'),
    url(r'^vote/$', views.vote, name='vote'),
    url(
        r'^raw/$',
        views.raw_page,
        name='raw'
    ),
    url(
        r'^review/$',
        views.review_page,
        name='review'
    )
]
