"""Users URL configuration"""

from django.contrib.auth.views import (
    LogoutView,
    LoginView,
    PasswordChangeView,
    PasswordChangeDoneView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)
from django.urls import path, reverse_lazy

from . import views


app_name = 'users'


urlpatterns = [
    # Деавторизация.
    path(
        'logout/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logout'
    ),
    # Регистрация пользователей.
    path(
        'signup/',
        views.SignUp.as_view(),
        name='signup'
    ),
    # Авторизация.
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    ),
    # Смена пароля: задать новый пароль.
    path(
        'password_change/',
        PasswordChangeView.as_view(
            template_name='users/password_change_form.html',
            success_url=reverse_lazy('users:password_change_done')
        ),
        name='password_change_form'
    ),
    # Смена пароля: уведомление об удачной смене пароля.
    path(
        'password_change/done/',
        PasswordChangeDoneView.as_view(
            template_name='users/password_change_done.html'
        ),
        name='password_change_done'
    ),
    # Восстановление пароля: Форма для восстановления пароля через email.
    path(
        'password_reset/',
        PasswordResetView.as_view(
            template_name='users/password_reset_form.html',
            success_url=reverse_lazy('users:password_reset_done')
        ),
        name='password_reset_form'
    ),
    # Восстановление пароля: уведомление об отправке ссылки для
    # восстановления пароля на email.
    path(
        'password_reset/done/',
        PasswordResetDoneView.as_view(
            template_name='users/password_reset_done.html'
        ),
        name='password_reset_done'
    ),
    # Восстановление пароля: страница подтверждения сброса пароля;
    # пользователь попадает сюда по ссылке из письма
    path(
        'reset/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html',
            success_url=reverse_lazy('users:password_reset_complete')
        ),
        name='password_reset_confirm'
    ),
    # Восстановление пароля: уведомление о том, что пароль изменён
    path(
        'reset/done/',
        PasswordResetCompleteView.as_view(
            template_name='users/password_reset_complete.html'
        ),
        name='password_reset_complete'
    ),
]
