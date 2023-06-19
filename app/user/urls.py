"""
URL mapping for the user API.
"""
from django.urls import path
from user import views


app_name = "user"

urlpatterns = [
    # ex: api/user/
    # POST, GET
    path('create/', views.CreateUserView.as_view(), name='create'),
    # ex: api/user/
    # POST
    path('token/', views.CreateTokenView.as_view(), name='token'),
    # ex: api/user/
    # GET, PUT, PATCH
    path('me/', views.ManageUserView.as_view(), name='me'),
]
