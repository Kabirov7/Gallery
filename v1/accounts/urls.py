from django.conf.urls import url

from v1.accounts.views.auth import register_user, login, profile

urlpatterns = [
    url(r'^register$', register_user, name='registration'),
    url(r'^login', login, name='login'),
    url(r'^profile', profile, name='profile')
]
