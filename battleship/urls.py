from django.conf.urls import patterns, include, url

from battleship import views

urlpatterns = patterns('',
    url(r'^$', views.game_preferences, name='game_preferences'),
    url(r'^game/$', views.game, name='game'),
    url(r'^startgame/$', views.startgame, name='startgame'),
    url(r'^turn/$', views.turn, name='turn'),
    url(r'^wait/$', views.waiting, name='waiting'),
)
