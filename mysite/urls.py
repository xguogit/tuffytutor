"""practice URL Configuration

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
from django.conf.urls import include, url
from django.contrib import admin
from mysite.titan import views, profile_views
admin.autodiscover()

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', views.index),
    url(r'^register/$', views.register),
    url(r'^test/$', views.test),
    url(r'^logout/$', views.logout),
    url(r'^profile/$', profile_views.profile),
    url(r'^edit_profile/$', profile_views.edit_profile),
    url(r'^course/(?P<course_id>\w{0,50})/$', profile_views.course),
    url(r'^course/(?P<course_id>\w{0,50})/post_question/$', profile_views.post_question),
    url(r'^course/(?P<course_id>\w{0,50})/question/(?P<question_id>\w{0,50})/$', profile_views.question),
    url(r'^add_current_course/$', profile_views.add_current_course),
    url(r'^add_previous_course/$', profile_views.add_previous_course),
    url(r'^add_hangout/$', profile_views.add_hangout),
    url(r'^message/$', profile_views.message),
    url(r'^new_message/$', profile_views.new_message),
    url(r'^hangout/(?P<hangout_id>\w{0,50})/$', profile_views.hangout),
    url(r'^course_list/$', profile_views.course_list),
    url(r'^badge/(?P<user_id>\w{0,50})/$', profile_views.badge),
    url(r'^message/(?P<message_id>\w{0,50})/reply/$', profile_views.reply),
]