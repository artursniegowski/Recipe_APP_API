"""
Views for the user API.
"""
from rest_framework import generics, authentication, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from user.serializers import (
    UserSeriazlier,
    AuthTokenSerializer,
)


class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system."""
    serializer_class = UserSeriazlier


class CreateTokenView(ObtainAuthToken):
    """Create a new auth token for user."""
    # we using the ObtainAuthToken provided by the authtoken DRF
    # and we are customizing the serialzier to use the custom serializer
    # tht we created -
    # so it returns data, validates etc like we defined in our serializer
    serializer_class = AuthTokenSerializer
    # so we makign  sure the brosable api is added, basiacaly overding this
    # with our settings from django file
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class ManageUserView(generics.RetrieveUpdateAPIView):
    """Manage the authenticated user."""
    # this view will accept GET, PUT, PATCH HTTP methods
    serializer_class = UserSeriazlier
    # making sure the token authentication is used !
    authentication_classes = [authentication.TokenAuthentication]
    # making sure the request user is authenticated
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        """Retrive and return the authenticated user"""
        # the user who we return has to be authenticated based on the
        # classes that we set above
        return self.request.user
