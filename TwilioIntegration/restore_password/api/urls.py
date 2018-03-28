from django.conf.urls import url

from .views import PasswordResetConfirmView, PasswordResetView

urlpatterns = [
    url(r'^password/reset/$', PasswordResetView.as_view(),
        name='rest_password_reset'),
    url(r'^password/reset/confirm/$', PasswordResetConfirmView.as_view(),
        name='rest_password_reset_confirm'),
    ]
