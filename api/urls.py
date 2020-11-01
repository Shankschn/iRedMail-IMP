from django.urls import path

from api import views

urlpatterns = [
    # path('', )
    path('change_user_status/', views.change_user_status),
    path('reset_user_password/', views.reset_user_password)
]